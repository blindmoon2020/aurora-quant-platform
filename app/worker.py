import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "aurora_worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

@celery_app.task(name="execute_async_rebalance")
def execute_async_rebalance(portfolio_id: int):
    print(f"[AURORA QUANT ENGINE] Executing automated risk-parity rebalance for portfolio {portfolio_id}")
    return {"status": "success", "portfolio_id": portfolio_id}
