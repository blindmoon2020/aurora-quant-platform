"""Intermarket Correlation Analysis Engine for Aurora Platform.
Measures rolling correlation between US Dollar Index (DXY), Gold (XAUUSD), and Crypto (BTC).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import math


@dataclass(frozen=True)
class IntermarketState:
    primary_symbol: str
    dxy_trend: str                # "BULLISH_STRONG", "BEARISH_STRONG", "NEUTRAL"
    correlation_with_dxy: float   # Range [-1.0, 1.0]
    market_regime: str            # "NORMAL_INVERSE", "CO_MOVING_ANOMALY", "DECOUPLED"
    macro_adjustment_score: float # Multiplier to adjust trading confidence


class IntermarketCorrelationEngine:
    """Evaluates intermarket dynamics, focusing on DXY impact on precious metals and digital assets."""

    @staticmethod
    def calculate_pearson_correlation(series_a: List[float], series_b: List[float]) -> float:
        n = min(len(series_a), len(series_b))
        if n < 5:
            return 0.0

        a = series_a[-n:]
        b = series_b[-n:]

        mean_a = sum(a) / n
        mean_b = sum(b) / n

        num = sum((a[i] - mean_a) * (b[i] - mean_b) for i in range(n))
        den_a = math.sqrt(sum((x - mean_a) ** 2 for x in a))
        den_b = math.sqrt(sum((y - mean_b) ** 2 for y in b))

        if den_a == 0 or den_b == 0:
            return 0.0

        return round(num / (den_a * den_b), 3)

    def analyze_intermarket_impact(
        self,
        target_symbol: str,
        target_prices: List[float],
        dxy_prices: List[float],
    ) -> IntermarketState:
        """Analyzes how DXY shifts impact Gold, Silver, or Crypto assets."""
        corr = self.calculate_pearson_correlation(target_prices, dxy_prices)
        
        # Determine DXY trend from recent prices
        dxy_trend = "NEUTRAL"
        if len(dxy_prices) >= 2:
            if dxy_prices[-1] > dxy_prices[-5]:
                dxy_trend = "BULLISH_STRONG"
            elif dxy_prices[-1] < dxy_prices[-5]:
                dxy_trend = "BEARISH_STRONG"

        # Regime classification
        sym = target_symbol.upper()
        if "XAU" in sym or "BTC" in sym:
            # Traditionally, Gold and BTC have negative correlation with DXY
            if corr < -0.3:
                regime = "NORMAL_INVERSE"
                score = 1.2  # High confidence when DXY and asset move inversely as expected
            elif corr > 0.3:
                regime = "CO_MOVING_ANOMALY"
                score = 0.7  # Anomaly warning (e.g., both rising due to extreme inflation panic)
            else:
                regime = "DECOUPLED"
                score = 1.0
        else:
            regime = "DECOUPLED"
            score = 1.0

        return IntermarketState(
            primary_symbol=sym,
            dxy_trend=dxy_trend,
            correlation_with_dxy=corr,
            market_regime=regime,
            macro_adjustment_score=score,
        )
