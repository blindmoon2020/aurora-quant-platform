from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class ClientPortfolioModel(Base):
    __tablename__ = "client_portfolios"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(120), index=True, nullable=False, default="عزیز انصاری")
    base_currency = Column(String(10), nullable=False, default="USD")
    aav_capital = Column(Float, nullable=False, default=50000.0)
    psych_score = Column(Integer, nullable=False, default=8)
    risk_profile = Column(String(80), nullable=False, default="Institutional Balanced")
    is_verified = Column(Boolean, nullable=False, default=False)
    is_psych_locked = Column(Boolean, nullable=False, default=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class ImmutableAuditLog(Base):
    __tablename__ = "immutable_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(120), index=True, nullable=False, default="عزیز انصاری")
    action_type = Column(String(60), nullable=False)
    details = Column(String(500), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False)
