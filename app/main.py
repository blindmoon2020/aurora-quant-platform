import os
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import engine, Base, get_db
from app.models import ClientPortfolioModel, ImmutableAuditLog
from app.worker import execute_async_rebalance

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Aurora Institutional Quant API",
    version="3.1.0",
    description="Backend Core for Global Asset Management & Multi-Asset Trading"
)


class PsychTestRequest(BaseModel):
    risk_score: int = Field(..., ge=1, le=12)
    client_name: str = Field(default="عزیز انصاری", min_length=1, max_length=120)
    force_override: bool = False


class CapitalUpdateRequest(BaseModel):
    new_aav: float = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=2, max_length=10)
    client_name: str = Field(default="عزیز انصاری", min_length=1, max_length=120)


def resolve_profile(score: int) -> str:
    if score <= 6 and score != 1:
        return "Ultra-Conservative"
    if score == 1:
        return "Ultra-Conservative"
    if score >= 10:
        return "Dynamic Alpha"
    return "Institutional Balanced"


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
    return {"status": "ok", "service": "aurora-quant-core", "version": "3.1.0"}


@app.post("/api/v3/auth/verify-psych")
def verify_psych_test(data: PsychTestRequest, db: Session = Depends(get_db)):
    portfolio = get_client_record(db, data.client_name)

    # اگر تست قبلاً تایید و قفل شده باشد و درخواست بازنگری صریح داده نشده باشد، تغییر نمی‌کند
    if portfolio and is_verified_and_locked(portfolio) and not data.force_override:
        db.commit()
        return {
            "success": True,
            "locked": True,
            "message": "Psychometric Profile Locked in Core",
            "profile": portfolio.risk_profile
        }

    profile = resolve_profile(data.risk_score)

    if not portfolio:
        kwargs = {
            "client_name": data.client_name,
            "risk_profile": profile,
        }
        if hasattr(ClientPortfolioModel, "is_psych_locked"):
            kwargs["is_psych_locked"] = True
        if hasattr(ClientPortfolioModel, "is_verified"):
            kwargs["is_verified"] = True
        if hasattr(ClientPortfolioModel, "psych_score"):
            kwargs["psych_score"] = data.risk_score

        portfolio = ClientPortfolioModel(**kwargs)
        db.add(portfolio)
    else:
        portfolio.client_name = data.client_name
        portfolio.risk_profile = profile
        if hasattr(portfolio, "psych_score"):
            portfolio.psych_score = data.risk_score
        set_verified_lock(portfolio, True)

    audit = ImmutableAuditLog(
        action_type="PSYCH_VERIFY",
        details=f"Client={data.client_name} | Profile={profile} | Override={data.force_override}"
    )
    db.add(audit)
    db.commit()
    db.refresh(portfolio)

    return {
        "success": True,
        "locked": True,
        "message": "Vault Unlocked via Secure Backend",
        "profile": portfolio.risk_profile
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
        "locked": True,
        "assets": [
            {"symbol": "XAUUSD", "exchange": "COMEX", "target": 30},
            {"symbol": "BRENT", "exchange": "ICE", "target": 20},
            {"symbol": "NAS100", "exchange": "NASDAQ", "target": 15}
        ]
    }


@app.post("/api/v3/portfolio/update-capital")
def update_capital(data: CapitalUpdateRequest, db: Session = Depends(get_db)):
    portfolio = get_client_record(db, data.client_name)
    currency_upper = data.currency.upper()

    if not portfolio:
        portfolio = ClientPortfolioModel(
            client_name=data.client_name,
            aav_capital=data.new_aav,
            base_currency=currency_upper
        )
        db.add(portfolio)
    else:
        portfolio.aav_capital = data.new_aav
        portfolio.base_currency = currency_upper

    audit = ImmutableAuditLog(
        action_type="CAPITAL_UPDATE",
        details=f"Client={portfolio.client_name} | AAV={data.new_aav} | Currency={currency_upper}"
    )
    db.add(audit)
    db.commit()
    db.refresh(portfolio)

    return {
        "success": True,
        "active_aav": portfolio.aav_capital,
        "currency": portfolio.base_currency
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
        "message": "Automated Rebalancing Task Dispatched"
    }


if os.path.isdir("public"):
    app.mount("/", StaticFiles(directory="public", html=True), name="public")
