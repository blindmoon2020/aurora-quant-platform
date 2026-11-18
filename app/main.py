from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import engine, Base, get_db
from app.models import ClientPortfolioModel, ImmutableAuditLog
from app.worker import execute_async_rebalance

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Aurora Institutional Quant API",
    version="3.0.0",
    description="Backend Core for Global Asset Management & Multi-Asset Trading"
)

class PsychTestRequest(BaseModel):
    risk_score: int
    client_name: str = "عزیز انصاری"

class CapitalUpdateRequest(BaseModel):
    new_aav: float
    currency: str

@app.post("/api/v3/auth/verify-psych")
def verify_psych_test(data: PsychTestRequest, db: Session = Depends(get_db)):
    profile = "Ultra-Conservative" if data.risk_score == 1 else "Institutional Balanced"

    portfolio = db.query(ClientPortfolioModel).first()
    if not portfolio:
        portfolio = ClientPortfolioModel(client_name=data.client_name, risk_profile=profile, is_verified=True)
        db.add(portfolio)
    else:
        portfolio.is_verified = True
        portfolio.risk_profile = profile

    audit = ImmutableAuditLog(action_type="PSYCH_VERIFY", details=f"Client verified with profile: {profile}")
    db.add(audit)
    db.commit()

    return {"success": True, "message": "Vault Unlocked via Secure Backend", "profile": profile}

@app.get("/api/v3/portfolio/data")
def get_portfolio_data(db: Session = Depends(get_db)):
    portfolio = db.query(ClientPortfolioModel).first()
    if not portfolio or not portfolio.is_verified:
        raise HTTPException(status_code=403, detail="Zero-Trust Access Denied: KYC Required")

    return {
        "client": portfolio.client_name,
        "currency": portfolio.base_currency,
        "aav": portfolio.aav_capital,
        "profile": portfolio.risk_profile,
        "assets": [
            {"symbol": "XAUUSD", "exchange": "COMEX", "target": 30},
            {"symbol": "BRENT", "exchange": "ICE", "target": 20},
            {"symbol": "NAS100", "exchange": "NASDAQ", "target": 15}
        ]
    }

@app.post("/api/v3/portfolio/update-capital")
def update_capital(data: CapitalUpdateRequest, db: Session = Depends(get_db)):
    portfolio = db.query(ClientPortfolioModel).first()
    if not portfolio:
        portfolio = ClientPortfolioModel(aav_capital=data.new_aav, base_currency=data.currency)
        db.add(portfolio)
    else:
        portfolio.aav_capital = data.new_aav
        portfolio.base_currency = data.currency

    db.commit()
    return {"success": True, "active_aav": portfolio.aav_capital, "currency": portfolio.base_currency}

@app.post("/api/v3/portfolio/trigger-rebalance")
def trigger_rebalance(db: Session = Depends(get_db)):
    portfolio = db.query(ClientPortfolioModel).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    task = execute_async_rebalance.delay(portfolio.id)
    return {"success": True, "task_id": task.id, "message": "Automated Rebalancing Task Dispatched"}
