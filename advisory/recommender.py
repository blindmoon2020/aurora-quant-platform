"""Advanced Technical Analysis Engine and Autonomous Robo-Advisory Recommender.
Synthesizes Multi-Asset technicals, fundamental sentiment, and strict risk guardrails
to generate institutional-grade buy/sell recommendations and portfolio allocations.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from aurora.core.asset_universe import AssetSpec, AssetUniverse
from aurora.data.news_calendar import MacroNewsHub


@dataclass(frozen=True)
class TechnicalIndicators:
    ema_20: float
    ema_40: float
    ema_200: float
    rsi_14: float
    volume_surge: bool
    price_action_pattern: str   # "PIN_BAR", "ENGULFING_BULLISH", "INSIDE_BAR", "NONE"


@dataclass(frozen=True)
class InvestmentRecommendation:
    symbol: str
    action: str                 # "STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"
    confidence_score: float     # 0.0 to 1.0
    suggested_entry: float
    stop_loss: float
    take_profit_1: float        # Risk-to-Reward 1:2
    take_profit_2: float        # Risk-to-Reward 1:3
    rationale: List[str] = field(default_factory=list)
    news_lockout_warning: Optional[str] = None


class AdvancedAdvisorEngine:
    """Institutional-grade advisory engine combining technical indicators, sentiment, and risk rules."""

    def __init__(self, universe: AssetUniverse, news_hub: Optional[MacroNewsHub] = None) -> None:
        self.universe = universe
        self.news_hub = news_hub

    def evaluate_asset(
        self,
        symbol: str,
        current_price: float,
        technicals: TechnicalIndicators,
        custom_currencies: Optional[List[str]] = None,
    ) -> InvestmentRecommendation:
        """Evaluates an asset across all dimensions and generates actionable recommendations."""
        spec = self.universe.get(symbol)
        name = spec.name if spec else symbol
        rationale: List[str] = []
        score = 0.5  # Neutral starting baseline

        # 1. Check Macroeconomic News Lockout if news hub is present
        lockout_warning = None
        if self.news_hub and spec:
            ccys = custom_currencies or [spec.currency, "USD"]
            lockout_warning = self.news_hub.active_news_lockout(ccys)
            if lockout_warning:
                rationale.append(f"WARNING: News Lockout Active -> {lockout_warning}")
                score -= 0.3

        # 2. Technical Trend Analysis (EMA Stacking)
        if technicals.ema_20 > technicals.ema_40 > technicals.ema_200:
            score += 0.2
            rationale.append("Bullish EMA Alignment (20 > 40 > 200).")
        elif technicals.ema_20 < technicals.ema_40 < technicals.ema_200:
            score -= 0.2
            rationale.append("Bearish EMA Alignment (20 < 40 < 200).")

        # 3. RSI & Momentum Filter
        if technicals.rsi_14 < 35:
            score += 0.15
            rationale.append(f"RSI oversold zone ({technicals.rsi_14:.1f}), potential bounce.")
        elif technicals.rsi_14 > 65:
            score -= 0.15
            rationale.append(f"RSI overbought zone ({technicals.rsi_14:.1f}), caution advised.")

        # 4. Price Action Patterns
        if technicals.price_action_pattern in ("PIN_BAR", "ENGULFING_BULLISH"):
            score += 0.2
            rationale.append(f"Strong bullish price action detected: {technicals.price_action_pattern}.")
        elif technicals.price_action_pattern == "ENGULFING_BEARISH":
            score -= 0.2
            rationale.append("Bearish engulfing pattern detected.")

        # 5. Fundamental News Sentiment Integration
        if self.news_hub and spec:
            tags = spec.tags + [spec.category.value]
            sentiment = self.news_hub.aggregate_sentiment(tag=tags[0] if tags else None)
            score += (sentiment * 0.2)
            rationale.append(f"Fundamental sentiment score: {sentiment:+.2f}")

        # Normalize score between 0.0 and 1.0
        confidence = max(0.0, min(1.0, score))

        # Determine Action & Risk-to-Reward Ratios (1:2 and 1:3 constraints)
        if confidence >= 0.75:
            action = "STRONG_BUY"
        elif confidence >= 0.60:
            action = "BUY"
        elif confidence <= 0.25:
            action = "STRONG_SELL"
        elif confidence <= 0.40:
            action = "SELL"
        else:
            action = "HOLD"

        # Calculate strict risk-to-reward boundaries
        atr_proxy = current_price * 0.015  # 1.5% volatility estimation buffer
        if "BUY" in action:
            stop_loss = round(current_price - atr_proxy, 4)
            tp1 = round(current_price + (atr_proxy * 2.0), 4)  # 1:2 R:R
            tp2 = round(current_price + (atr_proxy * 3.0), 4)  # 1:3 R:R
        elif "SELL" in action:
            stop_loss = round(current_price + atr_proxy, 4)
            tp1 = round(current_price - (atr_proxy * 2.0), 4)
            tp2 = round(current_price - (atr_proxy * 3.0), 4)
        else:
            stop_loss = round(current_price - atr_proxy, 4)
            tp1 = round(current_price + (atr_proxy * 2.0), 4)
            tp2 = round(current_price + (atr_proxy * 3.0), 4)

        return InvestmentRecommendation(
            symbol=symbol.upper(),
            action=action,
            confidence_score=round(confidence, 2),
            suggested_entry=current_price,
            stop_loss=stop_loss,
            take_profit_1=tp1,
            take_profit_2=tp2,
            rationale=rationale,
            news_lockout_warning=lockout_warning,
        )

    def scan_portfolio(self, market_data: Dict[str, tuple[float, TechnicalIndicators]]) -> List[InvestmentRecommendation]:
        """Scans multiple assets across global markets and outputs sorted investment recommendations."""
        recommendations = []
        for symbol, (price, tech) in market_data.items():
            rec = self.evaluate_asset(symbol, price, tech)
            recommendations.append(rec)
        # Sort by confidence score descending
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        return recommendations
