import os
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import engine, Base, get_db
from app.models import ClientPortfolioModel, ImmutableAuditLog, LinkedAccountModel
from app.worker import execute_async_rebalance

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Aurora Institutional Quant API",
    version="3.2.0",
    description="Persistent Core API for Aurora Smart Wealth & Multi-Asset Platform"
)


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
    if score <= 6:
        return {
            "profile": "Ultra-Conservative",
            "daily_dd_limit_pct": 2.0,
            "max_dd_limit_pct": 5.0,
        }
    if score >= 10:
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
    return {"status": "ok", "service": "aurora-quant-core", "version": "3.2.0"}


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
        "assets": [
            {"symbol": "XAUUSD", "exchange": "COMEX", "target": 30},
            {"symbol": "BRENT", "exchange": "ICE", "target": 20},
            {"symbol": "NAS100", "exchange": "NASDAQ", "target": 15},
        ],
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

    task = execute_async_rebalance.delay(portfolio.id)
    return {
        "success": True,
        "task_id": task.id,
        "message": "Automated Rebalancing Task Dispatched",
    }


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


if os.path.isdir("public"):
    app.mount("/", StaticFiles(directory="public", html=True), name="public")
