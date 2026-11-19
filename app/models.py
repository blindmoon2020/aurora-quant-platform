from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class ClientPortfolioModel(Base):
    __tablename__ = "client_portfolios"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(120), index=True, nullable=False, default="عبدالعزیز انصاری")
    base_currency = Column(String(10), nullable=False, default="USD")
    aav_capital = Column(Float, nullable=False, default=50000.0)
    psych_score = Column(Integer, nullable=False, default=8)
    risk_profile = Column(String(80), nullable=False, default="Institutional Balanced")
    daily_dd_limit_pct = Column(Float, nullable=False, default=3.0)
    max_dd_limit_pct = Column(Float, nullable=False, default=8.0)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_psych_locked = Column(Boolean, nullable=False, default=False)
    two_fa_enabled = Column(Boolean, nullable=False, default=True)
    anti_phishing_enabled = Column(Boolean, nullable=False, default=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class LinkedAccountModel(Base):
    __tablename__ = "linked_accounts"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(120), index=True, nullable=False, default="عبدالعزیز انصاری")
    provider_name = Column(String(80), nullable=False)
    account_label = Column(String(120), nullable=False)
    masked_iban = Column(String(40), nullable=False)
    is_verified = Column(Boolean, nullable=False, default=True)
    is_active = Column(Boolean, nullable=False, default=True)
    two_fa_enabled = Column(Boolean, nullable=False, default=True)
    anti_phishing_enabled = Column(Boolean, nullable=False, default=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class ImmutableAuditLog(Base):
    __tablename__ = "immutable_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(120), index=True, nullable=False, default="عبدالعزیز انصاری")
    action_type = Column(String(60), nullable=False)
    details = Column(String(500), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False)
