import logging
import math
import os
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import ClientPortfolioModel, ImmutableAuditLog, LinkedAccountModel
from app.worker import execute_async_rebalance

try:
    from app.risk_engine import (
        align_risk_with_psych_profile as _external_align_risk,
        build_correlation_matrix as _external_corr_matrix,
        compute_portfolio_var as _external_compute_var,
    )
except ImportError:
    _external_align_risk = None
    _external_corr_matrix = None
    _external_compute_var = None

try:
    from app.execution_bridge import evaluate_execution_readiness as _external_eval_readiness
except ImportError:
    _external_eval_readiness = None

logger = logging.getLogger("aurora.main")

try:
    Base.metadata.create_all(bind=engine)
except Exception as exc:
    logger.warning(f"[AURORA CORE] Database metadata initialization deferred: {exc}")

app = FastAPI(
    title="Aurora Institutional Quant API",
    version="3.5.0",
    description="Persistent Core API for Aurora Smart Wealth & Multi-Asset Platform",
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    return response


class PsychTestRequest(BaseModel):
    risk_score: int = Field(..., ge=1, le=12)
    client_name: str = Field(default="عبدالعزیز انصاری", min_length=1, max_length=120)
    force_override: bool = False


class CapitalUpdateRequest(BaseModel):
    new_aav: float = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=2, max_length=10)
    client_name: str = Field(default="عبدالعزیز انصاری", min_length=1, max_length=120)


class LinkedAccountCreateRequest(BaseModel):
    client_name: str = Field(default="عبدالعزیز انصاری", min_length=1, max_length=120)
    provider_name: str = Field(..., min_length=2, max_length=80)
    account_label: str = Field(..., min_length=2, max_length=120)
    raw_iban: str = Field(..., min_length=4, max_length=40)
    two_fa_enabled: bool = True
    anti_phishing_enabled: bool = True


def resolve_risk_config(score: int) -> dict:
    clamped = max(1, min(12, int(score)))
    if clamped <= 6:
        return {
            "profile": "Ultra-Conservative",
            "daily_dd_limit_pct": 2.0,
            "max_dd_limit_pct": 5.0,
        }
    if clamped >= 10:
        return {
            "profile": "Dynamic Alpha",
            "daily_dd_limit_pct": 5.0,
            "max_dd_limit_pct": 12.0,
        }
    return {
        "profile": "Institutional Balanced",
        "daily_dd_limit_pct": 3.0,
        "max_dd_limit_pct": 8.0,
    }


def _resolve_target_assets(score: int) -> List[dict]:
    clamped = max(1, min(12, int(score)))
    if clamped <= 6:
        weights = [45, 15, 25, 10, 5]
    elif clamped >= 10:
        weights = [15, 25, 15, 40, 5]
    else:
        weights = [30, 20, 20, 20, 10]

    meta = [
        ("XAUUSD", "COMEX"),
        ("BRENT", "ICE"),
        ("WHEAT", "CBOT"),
        ("NAS100", "NASDAQ"),
        ("EURUSD", "FOREX"),
    ]
    return [
        {"symbol": sym, "exchange": exch, "target": w}
        for (sym, exch), w in zip(meta, weights)
    ]


def _fallback_align_risk(psych_score: int, aav_capital: float) -> dict:
    clamped_score = max(1, min(12, int(psych_score)))
    cfg = resolve_risk_config(clamped_score)
    if clamped_score <= 6:
        weights = [0.45, 0.15, 0.25, 0.10, 0.05]
        herd_guard = "فعال — محدودیت سخت‌گیرانه در برابر نوسانات ناگهانی"
        glass_box_reasoning = "اولویت حفظ سرمایه و کنترل شدید افت روزانه بر اساس پروفایل محافظه‌کارانه."
    elif clamped_score >= 10:
        weights = [0.15, 0.25, 0.15, 0.40, 0.05]
        herd_guard = "فعال — کنترل اهرم و هشدار تمرکز بیش از حد"
        glass_box_reasoning = "تخصیص پویاتر با حفظ سقف‌های تعریف‌شده برای جلوگیری از افت کنترل‌نشده."
    else:
        weights = [0.30, 0.20, 0.20, 0.20, 0.10]
        herd_guard = "فعال — تعادل میان حفظ سرمایه و بازده هدف"
        glass_box_reasoning = "توازن نظام‌مند میان نقدشوندگی، طلا/کالا و شاخص‌ها بر اساس پروفایل متعادل."

    vols = [0.012, 0.018, 0.015, 0.020, 0.009]
    if _external_compute_var:
        var_95 = _external_compute_var(aav_capital, weights, vols, confidence_z=1.65)
    else:
        portfolio_vol = math.sqrt(max(0.0, sum((w * v) ** 2 for w, v in zip(weights, vols))))
        var_95 = round(aav_capital * portfolio_vol * 1.65, 2)

    daily_loss_cap = round(aav_capital * (cfg["daily_dd_limit_pct"] / 100.0), 2)
    max_loss_amount = round(aav_capital * (cfg["max_dd_limit_pct"] / 100.0), 2)

    return {
        "risk_profile": cfg["profile"],
        "daily_dd_limit_pct": cfg["daily_dd_limit_pct"],
        "max_dd_limit_pct": cfg["max_dd_limit_pct"],
        "daily_loss_cap_amount": daily_loss_cap,
        "max_loss_stress_amount": max_loss_amount,
        "var_95": var_95,
        "behavioral_herd_guard": herd_guard,
        "glass_box_reasoning": glass_box_reasoning,
    }


def _fallback_corr_matrix(symbols: List[str]) -> Dict[str, Dict[str, float]]:
    matrix: Dict[str, Dict[str, float]] = {}
    for s1 in symbols:
        u1 = s1.upper()
        matrix[s1] = {}
        for s2 in symbols:
            u2 = s2.upper()
            if s1 == s2:
                matrix[s1][s2] = 1.0
            elif ("XAU" in u1 and "USD" in u2) or ("USD" in u1 and "XAU" in u2):
                matrix[s1][s2] = -0.35
            elif ("BRENT" in u1 and "WHEAT" in u2) or ("WHEAT" in u1 and "BRENT" in u2):
                matrix[s1][s2] = 0.25
            else:
                matrix[s1][s2] = 0.15
    return matrix


def _fallback_eval_readiness(
    client_name: str,
    aav_capital: float,
    risk_profile: str,
    is_psych_locked: bool,
    two_fa_enabled: bool,
    anti_phishing_enabled: bool,
    daily_dd_limit_pct: float,
    max_dd_limit_pct: float,
    linked_accounts_count: int,
) -> dict:
    blockers: List[str] = []
    warnings: List[str] = []
    if not is_psych_locked:
        blockers.append("آزمون روانشناسی و پروفایل ریسک در هسته قفل نشده است.")
    if not two_fa_enabled:
        blockers.append("تایید دو مرحله‌ای (2FA) فعال نیست.")
    if not anti_phishing_enabled:
        warnings.append("کد آنتی‌فیشینگ فعال نیست.")
    if aav_capital <= 0:
        blockers.append("سرمایه فعال (AAV) معتبر نیست.")
    if linked_accounts_count <= 0:
        warnings.append("هنوز هیچ حساب متصل و تاییدشده‌ای ثبت نشده است.")

    return {
        "client_name": client_name,
        "ready_for_controlled_execution": len(blockers) == 0,
        "risk_profile": risk_profile,
        "security_controls": {
            "two_fa_enabled": bool(two_fa_enabled),
            "anti_phishing_enabled": bool(anti_phishing_enabled),
            "psych_locked": bool(is_psych_locked),
            "withdrawal_blocked_by_policy": True,
        },
        "risk_guards": {
            "daily_dd_limit_pct": daily_dd_limit_pct,
            "max_dd_limit_pct": max_dd_limit_pct,
            "daily_loss_guard_amount": round(max(0.0, aav_capital) * (daily_dd_limit_pct / 100.0), 2),
            "max_loss_guard_amount": round(max(0.0, aav_capital) * (max_dd_limit_pct / 100.0), 2),
            "max_single_order_cap_amount": round(max(0.0, aav_capital) * 0.10, 2),
        },
        "linked_accounts_count": int(linked_accounts_count),
        "blockers": blockers,
        "warnings": warnings,
    }


def mask_sensitive_value(value: str, visible_tail: int = 4) -> str:
    cleaned = "".join(ch for ch in value.strip() if not ch.isspace())
    if len(cleaned) <= visible_tail:
        return "*" * len(cleaned)
    return ("*" * (len(cleaned) - visible_tail)) + cleaned[-visible_tail:]


def get_client_record(db: Session, client_name: Optional[str] = None) -> Optional[ClientPortfolioModel]:
    if client_name:
        record = db.query(ClientPortfolioModel).filter(ClientPortfolioModel.client_name == client_name).first()
        if record:
            return record
    return db.query(ClientPortfolioModel).order_by(ClientPortfolioModel.id.asc()).first()


def is_verified_and_locked(portfolio: ClientPortfolioModel) -> bool:
    return bool(getattr(portfolio, "is_psych_locked", False) or getattr(portfolio, "is_verified", False))


def set_verified_lock(portfolio: ClientPortfolioModel, locked: bool = True) -> None:
    if hasattr(portfolio, "is_psych_locked"):
        portfolio.is_psych_locked = locked
    if hasattr(portfolio, "is_verified"):
        portfolio.is_verified = locked


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "aurora-quant-core", "version": "3.5.0"}


@app.post("/api/v3/auth/verify-psych")
def verify_psych_test(data: PsychTestRequest, db: Session = Depends(get_db)):
    portfolio = get_client_record(db, data.client_name)

    if portfolio and is_verified_and_locked(portfolio) and not data.force_override:
        db.commit()
        return {
            "success": True,
            "locked": True,
            "message": "Psychometric Profile Locked in Core",
            "profile": portfolio.risk_profile,
            "daily_dd_limit_pct": portfolio.daily_dd_limit_pct,
            "max_dd_limit_pct": portfolio.max_dd_limit_pct,
        }

    cfg = resolve_risk_config(data.risk_score)
    profile = cfg["profile"]

    if not portfolio:
        portfolio = ClientPortfolioModel(
            client_name=data.client_name,
            psych_score=data.risk_score,
            risk_profile=profile,
            daily_dd_limit_pct=cfg["daily_dd_limit_pct"],
            max_dd_limit_pct=cfg["max_dd_limit_pct"],
            is_verified=True,
            is_psych_locked=True,
        )
        db.add(portfolio)
    else:
        portfolio.client_name = data.client_name
        portfolio.psych_score = data.risk_score
        portfolio.risk_profile = profile
        portfolio.daily_dd_limit_pct = cfg["daily_dd_limit_pct"]
        portfolio.max_dd_limit_pct = cfg["max_dd_limit_pct"]
        set_verified_lock(portfolio, True)

    db.add(
        ImmutableAuditLog(
            client_name=data.client_name,
            action_type="PSYCH_VERIFY",
            details=f"Client={data.client_name} | Profile={profile} | Override={data.force_override}",
        )
    )
    db.commit()
    db.refresh(portfolio)

    return {
        "success": True,
        "locked": True,
        "message": "Vault Unlocked via Secure Backend",
        "profile": portfolio.risk_profile,
        "daily_dd_limit_pct": portfolio.daily_dd_limit_pct,
        "max_dd_limit_pct": portfolio.max_dd_limit_pct,
    }


@app.get("/api/v3/portfolio/data")
def get_portfolio_data(client_name: Optional[str] = Query(default=None), db: Session = Depends(get_db)):
    portfolio = get_client_record(db, client_name)
    if not portfolio or not is_verified_and_locked(portfolio):
        raise HTTPException(status_code=403, detail="Zero-Trust Access Denied: KYC Required")

    score = getattr(portfolio, "psych_score", 8)
    return {
        "client": portfolio.client_name,
        "currency": portfolio.base_currency,
        "aav": portfolio.aav_capital,
        "profile": portfolio.risk_profile,
        "daily_dd_limit_pct": portfolio.daily_dd_limit_pct,
        "max_dd_limit_pct": portfolio.max_dd_limit_pct,
        "locked": True,
        "security": {
            "two_fa_enabled": portfolio.two_fa_enabled,
            "anti_phishing_enabled": portfolio.anti_phishing_enabled,
        },
        "assets": _resolve_target_assets(score),
    }


@app.get("/api/v3/portfolio/risk-report")
def get_risk_report(client_name: Optional[str] = Query(default=None), db: Session = Depends(get_db)):
    portfolio = get_client_record(db, client_name)
    if not portfolio or not is_verified_and_locked(portfolio):
        raise HTTPException(status_code=403, detail="Zero-Trust Access Denied: KYC Required")

    score = getattr(portfolio, "psych_score", 8)
    align_fn = _external_align_risk or _fallback_align_risk
    corr_fn = _external_corr_matrix or _fallback_corr_matrix
    metrics = align_fn(score, portfolio.aav_capital)
    symbols = ["XAUUSD", "BRENT", "WHEAT", "NAS100", "EURUSD"]

    return {
        "client": portfolio.client_name,
        "currency": portfolio.base_currency,
        "aav": portfolio.aav_capital,
        "risk_metrics": metrics,
        "correlation_matrix": corr_fn(symbols),
        "glass_box_note": "محاسبات ریسک، همبستگی و سقف افت سرمایه بر اساس پروفایل ثبت‌شده و بدون تصمیم هیجانی انجام شده است.",
    }


@app.post("/api/v3/portfolio/update-capital")
def update_capital(data: CapitalUpdateRequest, db: Session = Depends(get_db)):
    portfolio = get_client_record(db, data.client_name)
    currency_upper = data.currency.upper()

    if not portfolio:
        portfolio = ClientPortfolioModel(
            client_name=data.client_name,
            aav_capital=data.new_aav,
            base_currency=currency_upper,
        )
        db.add(portfolio)
    else:
        portfolio.aav_capital = data.new_aav
        portfolio.base_currency = currency_upper

    db.add(
        ImmutableAuditLog(
            client_name=portfolio.client_name,
            action_type="CAPITAL_UPDATE",
            details=f"Client={portfolio.client_name} | AAV={data.new_aav} | Currency={currency_upper}",
        )
    )
    db.commit()
    db.refresh(portfolio)

    return {
        "success": True,
        "active_aav": portfolio.aav_capital,
        "currency": portfolio.base_currency,
    }


@app.post("/api/v3/portfolio/trigger-rebalance")
def trigger_rebalance(client_name: Optional[str] = Query(default=None), db: Session = Depends(get_db)):
    portfolio = get_client_record(db, client_name)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    try:
        task = execute_async_rebalance.delay(portfolio.id)
        return {
            "success": True,
            "task_id": task.id,
            "message": "Automated Rebalancing Task Dispatched",
        }
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Rebalance worker queue unavailable: {exc}")


@app.get("/api/v3/execution/readiness")
def get_execution_readiness(client_name: Optional[str] = Query(default=None), db: Session = Depends(get_db)):
    portfolio = get_client_record(db, client_name)
    if not portfolio or not is_verified_and_locked(portfolio):
        raise HTTPException(status_code=403, detail="Zero-Trust Access Denied: KYC Required")

    acc_query = db.query(LinkedAccountModel)
    if client_name:
        acc_query = acc_query.filter(LinkedAccountModel.client_name == client_name)
    linked_count = acc_query.count()

    eval_fn = _external_eval_readiness or _fallback_eval_readiness
    readiness = eval_fn(
        client_name=portfolio.client_name,
        aav_capital=portfolio.aav_capital,
        risk_profile=portfolio.risk_profile,
        is_psych_locked=is_verified_and_locked(portfolio),
        two_fa_enabled=bool(getattr(portfolio, "two_fa_enabled", True)),
        anti_phishing_enabled=bool(getattr(portfolio, "anti_phishing_enabled", True)),
        daily_dd_limit_pct=float(getattr(portfolio, "daily_dd_limit_pct", 3.0)),
        max_dd_limit_pct=float(getattr(portfolio, "max_dd_limit_pct", 8.0)),
        linked_accounts_count=linked_count,
    )

    db.add(
        ImmutableAuditLog(
            client_name=portfolio.client_name,
            action_type="EXECUTION_READINESS_CHECK",
            details=(
                f"Client={portfolio.client_name} | Ready={readiness['ready_for_controlled_execution']} "
                f"| Accounts={linked_count}"
            ),
        )
    )
    db.commit()

    return readiness


@app.get("/api/v3/security/accounts")
def get_linked_accounts(client_name: Optional[str] = Query(default=None), db: Session = Depends(get_db)):
    portfolio = get_client_record(db, client_name)
    if not portfolio or not is_verified_and_locked(portfolio):
        raise HTTPException(status_code=403, detail="Zero-Trust Access Denied: KYC Required")

    query = db.query(LinkedAccountModel)
    if client_name:
        query = query.filter(LinkedAccountModel.client_name == client_name)
    accounts = query.order_by(LinkedAccountModel.id.asc()).all()

    return {
        "client": portfolio.client_name,
        "security_posture": {
            "two_fa_enabled": portfolio.two_fa_enabled,
            "anti_phishing_enabled": portfolio.anti_phishing_enabled,
            "psych_locked": True,
            "risk_profile": portfolio.risk_profile,
        },
        "accounts": [
            {
                "id": acc.id,
                "provider_name": acc.provider_name,
                "account_label": acc.account_label,
                "masked_iban": acc.masked_iban,
                "is_verified": acc.is_verified,
                "is_active": acc.is_active,
                "two_fa_enabled": acc.two_fa_enabled,
                "anti_phishing_enabled": acc.anti_phishing_enabled,
            }
            for acc in accounts
        ],
    }


@app.post("/api/v3/security/accounts")
def register_linked_account(data: LinkedAccountCreateRequest, db: Session = Depends(get_db)):
    portfolio = get_client_record(db, data.client_name)
    if not portfolio or not is_verified_and_locked(portfolio):
        raise HTTPException(status_code=403, detail="Zero-Trust Access Denied: KYC Required")

    masked_iban = mask_sensitive_value(data.raw_iban, visible_tail=4)
    account = LinkedAccountModel(
        client_name=data.client_name,
        provider_name=data.provider_name.strip(),
        account_label=data.account_label.strip(),
        masked_iban=masked_iban,
        is_verified=True,
        is_active=True,
        two_fa_enabled=data.two_fa_enabled,
        anti_phishing_enabled=data.anti_phishing_enabled,
    )
    db.add(account)
    db.add(
        ImmutableAuditLog(
            client_name=data.client_name,
            action_type="LINKED_ACCOUNT_REGISTERED",
            details=f"Provider={data.provider_name} | Label={data.account_label} | MaskedRef={masked_iban}",
        )
    )
    db.commit()
    db.refresh(account)

    return {
        "success": True,
        "account": {
            "id": account.id,
            "provider_name": account.provider_name,
            "account_label": account.account_label,
            "masked_iban": account.masked_iban,
            "is_verified": account.is_verified,
            "is_active": account.is_active,
        },
    }


@app.get("/api/v3/security/audit-logs")
def get_audit_logs(
    client_name: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    portfolio = get_client_record(db, client_name)
    if not portfolio or not is_verified_and_locked(portfolio):
        raise HTTPException(status_code=403, detail="Zero-Trust Access Denied: KYC Required")

    query = db.query(ImmutableAuditLog)
    if client_name:
        query = query.filter(ImmutableAuditLog.client_name == client_name)
    logs = query.order_by(ImmutableAuditLog.id.desc()).limit(limit).all()

    return {
        "client": portfolio.client_name,
        "logs": [
            {
                "id": log.id,
                "action_type": log.action_type,
                "details": log.details,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            }
            for log in logs
        ],
    }


if os.path.isdir("public"):
    app.mount("/", StaticFiles(directory="public", html=True), name="public")
