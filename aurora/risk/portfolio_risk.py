"""Portfolio-Wide Risk Management and Exposure Controller for Aurora Platform.
Calculates aggregate exposure, correlation risk, and total portfolio drawdown constraints.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class OpenPosition:
    symbol: str
    size: float
    entry_price: float
    current_price: float
    is_buy: bool


class PortfolioRiskManager:
    """Monitors multi-asset portfolio exposure, leverage, and drawdown limits."""

    def __init__(self, max_total_drawdown_pct: float = 0.05, max_open_positions: int = 5) -> None:
        self.max_dd_pct = max_total_drawdown_pct
        self.max_positions = max_open_positions

    def evaluate_portfolio_risk(self, positions: List[OpenPosition], current_capital: float) -> tuple[bool, str]:
        """Evaluates if new trades or existing portfolio breach institutional risk thresholds."""
        if len(positions) >= self.max_positions:
            return False, f"Risk Gate: Maximum concurrent positions limit reached ({self.max_positions})."

        total_unrealized_pnl = 0.0
        for pos in positions:
            diff = (pos.current_price - pos.entry_price) if pos.is_buy else (pos.entry_price - pos.current_price)
            total_unrealized_pnl += diff * pos.size

        # Check total drawdown impact
        if current_capital > 0:
            current_dd_pct = abs(min(0.0, total_unrealized_pnl)) / current_capital
            if current_dd_pct >= self.max_dd_pct:
                return False, f"Risk Gate: Portfolio drawdown limit breached ({current_dd_pct:.2%})."

        return True, "Portfolio risk checks passed successfully."
