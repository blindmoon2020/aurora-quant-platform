from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from app.database import Base

class ClientPortfolioModel(Base):
    __tablename__ = "client_portfolios"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String, default="عزیز انصاری")
    base_currency = Column(String, default="USD")
    aav_capital = Column(Float, default=50000.0)
    risk_profile = Column(String, default="Institutional Balanced")
    is_verified = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ImmutableAuditLog(Base):
    __tablename__ = "immutable_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String)
    details = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
