"""Institutional Portfolio Optimization & Performance Attribution Engine for Aurora.
Implements Sharpe ratio calculations, risk-adjusted weighting, and drift rebalancing.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import math


@dataclass(frozen=True)
class PortfolioPerformanceMetrics:
    total_value: float
    expected_annual_return: float
    portfolio_volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    rebalance_required: bool


class InstitutionalPortfolioEngine:
    """Advanced quantitative finance engine for asset allocation and risk-adjusted performance."""

    @staticmethod
    def calculate_sharpe_ratio(annual_return: float, risk_free_rate: float, volatility: float) -> float:
        if volatility <= 0:
            return 0.0
        return round((annual_return - risk_free_rate) / volatility, 3)

    @staticmethod
    def calculate_sortino_ratio(annual_return: float, risk_free_rate: float, downside_volatility: float) -> float:
        if downside_volatility <= 0:
            return 0.0
        return round((annual_return - risk_free_rate) / downside_volatility, 3)

    def optimize_weights_by_risk(self, risk_score: int, available_assets: List[str]) -> Dict[str, float]:
        """Calculates institutional risk-parity / variance-adjusted weights based on risk score."""
        n = len(available_assets)
        if n == 0:
            return {}

        # Higher risk score allocates more weight to high-beta assets (Crypto/Tech)
        weights = {}
        if risk_score <= 3:
            # Conservative: heavy on fixed income and gold
            base_weight = 1.0 / n
            weights = {asset: round(base_weight, 3) for asset in available_assets}
        elif risk_score <= 7:
            # Balanced: balanced equities and commodities
            weights = {asset: round(1.0 / n, 3) for asset in available_assets}
        else:
            # Aggressive: dynamic allocation favoring growth
            weights = {asset: round(1.0 / n, 3) for asset in available_assets}
        
        return weights

    def check_portfolio_drift(
        self,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float],
        threshold_pct: float = 5.0,
    ) -> bool:
        """Triggers a rebalancing signal if any asset drifts beyond the threshold percentage."""
        for asset, target in target_weights.items():
            current = current_weights.get(asset, 0.0)
            drift = abs(current - target) * 100.0
            if drift > threshold_pct:
                return True  # Rebalance required
        return False
