"""Advanced Quant Backtest & Statistical Performance Engine for Aurora.
Inspired by QuantConnect & VectorBT high-performance analytics.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class TradeResult:
    trade_id: str
    pnl: float
    return_pct: float


class AdvancedQuantEngine:
    @staticmethod
    def calculate_performance_metrics(trades: List[TradeResult]) -> dict:
        if not trades:
            return {"status": "No trades provided"}

        total_trades = len(trades)
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]

        win_rate = (len(winning_trades) / total_trades) * 100
        gross_profit = sum(t.pnl for t in winning_trades)
        gross_loss = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 1.0

        profit_factor = round(gross_profit / gross_loss, 2)
        net_pnl = sum(t.pnl for t in trades)

        return {
            "Total Trades": total_trades,
            "Win Rate (%)": round(win_rate, 2),
            "Profit Factor": profit_factor,
            "Net PnL ($)": round(net_pnl, 2)
        }


if __name__ == "__main__":
    print("[INFO] Running Advanced Quant Performance Audit...")
    sample_trades = [
        TradeResult("T-1", 1200.0, 2.4),
        TradeResult("T-2", -400.0, -0.8),
        TradeResult("T-3", 1800.0, 3.5),
        TradeResult("T-4", 950.0, 1.9)
    ]
    metrics = AdvancedQuantEngine.calculate_performance_metrics(sample_trades)
    for k, v in metrics.items():
        print(f" * {k}: {v}")
