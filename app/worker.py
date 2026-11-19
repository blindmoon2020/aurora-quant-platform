import logging
import os
from celery import Celery

logger = logging.getLogger("aurora.worker")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "aurora_worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
)


def _check_psych_lock_status(portfolio_id: int) -> dict:
    """بررسی وضعیت قفل تست روانشناسی در دیتابیس بدون ایجاد اختلال در محیط‌های بدون DB."""
    try:
        from app.database import SessionLocal
        from app.models import ClientPortfolioModel

        db = SessionLocal()
        try:
            portfolio = db.query(ClientPortfolioModel).filter(ClientPortfolioModel.id == portfolio_id).first()
            if not portfolio:
                return {"found": False, "locked": False, "profile": None}

            locked = bool(
                getattr(portfolio, "is_psych_locked", False) or getattr(portfolio, "is_verified", False)
            )
            return {
                "found": True,
                "locked": locked,
                "profile": getattr(portfolio, "risk_profile", None),
            }
        finally:
            db.close()
    except Exception as exc:
        logger.warning(f"[AURORA QUANT ENGINE] DB lock pre-check skipped for portfolio {portfolio_id}: {exc}")
        return {"found": True, "locked": True, "profile": None}


@celery_app.task(name="execute_async_rebalance")
def execute_async_rebalance(portfolio_id: int):
    lock_info = _check_psych_lock_status(portfolio_id)
    logger.info(
        f"[AURORA QUANT ENGINE] Executing automated risk-parity rebalance for portfolio {portfolio_id} "
        f"| psych_locked={lock_info['locked']} | profile={lock_info['profile']}"
    )
    print(f"[AURORA QUANT ENGINE] Executing automated risk-parity rebalance for portfolio {portfolio_id}")
    return {
        "status": "success",
        "portfolio_id": portfolio_id,
        "psych_locked": lock_info["locked"],
        "profile": lock_info["profile"],
    }
