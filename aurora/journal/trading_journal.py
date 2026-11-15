"""Institutional Trading Journal, Performance Reporting, and Analytics Engine
for Aurora Platform.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class TradeRecord:
    trade_id: str
    symbol: str
    side: str          # "BUY" or "SELL"
    entry_price: float
    exit_price: float
    volume: float
    pnl: float
    risk_reward_ratio: float
    strategy_tag: str
    timestamp_utc: int


@dataclass(frozen=True)
class JournalReport:
    total_trades: int
    win_rate_pct: float
    profit_factor: float
    net_pnl: float
    max_drawdown_amount: float
    expectancy: float


class TradingJournal:
    """Records, aggregates, and generates professional performance metrics for trades."""

    def __init__(self) -> None:
        self.trades: List[TradeRecord] = []

    def log_trade(self, trade: TradeRecord) -> None:
        self.trades.append(trade)

    def generate_report(self) -> JournalReport:
        if not self.trades:
            return JournalReport(0, 0.0, 0.0, 0.0, 0.0, 0.0)

        total = len(self.trades)
        wins = [t for t in self.trades if t.pnl > 0]
        losses = [t for t in self.trades if t.pnl <= 0]

        win_rate = (len(wins) / total) * 100.0
        gross_profit = sum(t.pnl for t in wins)
        gross_loss = abs(sum(t.pnl for t in losses))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (99.9 if gross_profit > 0 else 0.0)
        net_pnl = sum(t.pnl for t in self.trades)

        # Max drawdown calculation over trade sequence
        peak = 0.0
        cum_pnl = 0.0
        max_dd = 0.0
        for t in self.trades:
            cum_pnl += t.pnl
            if cum_pnl > peak:
                peak = cum_pnl
            dd = peak - cum_pnl
            if dd > max_dd:
                max_dd = dd

        avg_win = (gross_profit / len(wins)) if wins else 0.0
        avg_loss = (gross_loss / len(losses)) if losses else 0.0
        expectancy = ((len(wins) / total) * avg_win) - ((len(losses) / total) * avg_loss)

        return JournalReport(
            total_trades=total,
            win_rate_pct=round(win_rate, 2),
            profit_factor=round(profit_factor, 2),
            net_pnl=round(net_pnl, 2),
            max_drawdown_amount=round(max_dd, 2),
            expectancy=round(expectancy, 2),
        )
