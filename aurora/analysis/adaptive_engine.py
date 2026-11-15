"""Adaptive Multi-Asset Analysis Router for Aurora Platform.
Dynamically tailors technical indicators and weighting for Gold, Oil, Equities, and Crypto.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class AssetAnalysisProfile:
    asset_class: str
    primary_indicator: str
    volatility_multiplier: float
    news_sensitivity: str  # "HIGH", "MEDIUM", "LOW"
    recommended_stop_loss_atr_multiple: float


class AdaptiveAnalysisRouter:
    """Selects and tunes quantitative algorithms based on the specific asset class."""

    PROFILES: Dict[str, AssetAnalysisProfile] = {
        "GOLD": AssetAnalysisProfile(
            asset_class="Precious Metal",
            primary_indicator="Volume Profile + Liquidity Sweeps",
            volatility_multiplier=1.5,
            news_sensitivity="HIGH",
            recommended_stop_loss_atr_multiple=2.0,
        ),
        "OIL": AssetAnalysisProfile(
            asset_class="Energy Commodity",
            primary_indicator="Supply/Demand Zones + Inventory Fills",
            volatility_multiplier=2.0,
            news_sensitivity="HIGH",
            recommended_stop_loss_atr_multiple=2.5,
        ),
        "EQUITY": AssetAnalysisProfile(
            asset_class="Global Stock / Index",
            primary_indicator="EMA 50/200 + Market Structure BOS",
            volatility_multiplier=1.0,
            news_sensitivity="MEDIUM",
            recommended_stop_loss_atr_multiple=1.5,
        ),
        "CRYPTO": AssetAnalysisProfile(
            asset_class="Digital Asset",
            primary_indicator="Smart Money Traps + Order Block Retests",
            volatility_multiplier=3.0,
            news_sensitivity="HIGH",
            recommended_stop_loss_atr_multiple=3.0,
        ),
    }

    def get_profile(self, symbol: str) -> AssetAnalysisProfile:
        sym = symbol.upper()
        if "XAU" in sym or "GOLD" in sym:
            return self.PROFILES["GOLD"]
        elif "WTI" in sym or "BRENT" in sym or "OIL" in sym:
            return self.PROFILES["OIL"]
        elif "BTC" in sym or "ETH" in sym or "USDT" in sym:
            return self.PROFILES["CRYPTO"]
        else:
            return self.PROFILES["EQUITY"]
