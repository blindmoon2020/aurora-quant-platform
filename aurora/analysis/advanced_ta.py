"""Advanced Technical Analysis Engine for Aurora Platform.
Implements Market Structure (HH/HL/LH/LL), Dynamic EMAs (50/200), RSI filters,
Support/Resistance Flip Zones, and Candlestick Price Action Patterns (Pin Bar, Engulfing).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass(frozen=True)
class Candle:
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class MarketStructureResult:
    trend: str                  # "UPTREND", "DOWNTREND", "SIDEWAYS"
    market_structure: str       # "HH_HL" (Higher Highs/Lows), "LH_LL", "RANGE"
    ema_50: float
    ema_200: float
    rsi_14: float
    price_action_pattern: str   # "PIN_BAR", "ENGULFING_BULLISH", "ENGULFING_BEARISH", "NONE"
    key_support: float
    key_resistance: float
    recommended_entry_type: str # "PULLBACK_FLIP", "DYNAMIC_EMA_BOUNCE", "BREAKOUT", "WAIT"


class AdvancedTechnicalAnalyzer:
    """Computes institutional-grade technical analysis matching professional price-action rules."""

    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> float:
        if not prices:
            return 0.0
        if len(prices) < period:
            period = len(prices)
        multiplier = 2.0 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        return round(ema, 4)

    @staticmethod
    def calculate_rsi(closes: List[float], period: int = 14) -> float:
        if len(closes) < period + 1:
            return 50.0
        gains = []
        losses = []
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i - 1]
            gains.append(max(0.0, diff))
            losses.append(max(0.0, -diff))

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return round(rsi, 2)

    @staticmethod
    def detect_price_action(candle: Candle, prev_candle: Candle) -> str:
        """Detects Pin Bar or Engulfing patterns based on professional price action rules."""
        body = abs(candle.close - candle.open)
        total_range = candle.high - candle.low
        if total_range == 0:
            return "NONE"

        upper_shadow = candle.high - max(candle.close, candle.open)
        lower_shadow = min(candle.close, candle.open) - candle.low

        # Pin Bar detection (Long tail, small body)
        if lower_shadow >= (total_range * 0.6) and body <= (total_range * 0.3):
            return "PIN_BAR"
        if upper_shadow >= (total_range * 0.6) and body <= (total_range * 0.3):
            return "PIN_BAR"

        # Engulfing detection
        prev_body = abs(prev_candle.close - prev_candle.open)
        if candle.close > candle.open and prev_candle.close < prev_candle.open:
            if candle.close >= prev_candle.open and candle.open <= prev_candle.close:
                if body > prev_body:
                    return "ENGULFING_BULLISH"
        elif candle.close < candle.open and prev_candle.close > prev_candle.open:
            if candle.close <= prev_candle.open and candle.open >= prev_candle.close:
                if body > prev_body:
                    return "ENGULFING_BEARISH"

        return "NONE"

    @staticmethod
    def identify_market_structure(highs: List[float], lows: List[float]) -> str:
        """Identifies Higher Highs/Lows (Uptrend) or Lower Highs/Lows (Downtrend)."""
        if len(highs) < 4 or len(lows) < 4:
            return "RANGE"
        
        recent_highs = highs[-4:]
        recent_lows = lows[-4:]

        hh = recent_highs[-1] > recent_highs[-2] and recent_highs[-2] > recent_highs[-3]
        hl = recent_lows[-1] > recent_lows[-2] and recent_lows[-2] > recent_lows[-3]
        lh = recent_highs[-1] < recent_highs[-2] and recent_highs[-2] < recent_highs[-3]
        ll = recent_lows[-1] < recent_lows[-2] and recent_lows[-2] < recent_lows[-3]

        if hh and hl:
            return "HH_HL"
        elif lh and ll:
            return "LH_LL"
        return "RANGE"

    def analyze(self, candles: List[Candle]) -> MarketStructureResult:
        """Performs full institutional technical scan on candle history."""
        if not candles:
            raise ValueError("Candle history cannot be empty.")

        closes = [c.close for c in candles]
        highs = [c.high for c in candles]
        lows = [c.low for c in candles]

        ema_50 = self.calculate_ema(closes, 50)
        ema_200 = self.calculate_ema(closes, 200)
        rsi_14 = self.calculate_rsi(closes, 14)
        structure = self.identify_market_structure(highs, lows)

        pa_pattern = "NONE"
        if len(candles) >= 2:
            pa_pattern = self.detect_price_action(candles[-1], candles[-2])

        # Trend and Rule Determination
        if structure == "HH_HL" and ema_50 > ema_200 and rsi_14 >= 45:
            trend = "UPTREND"
            entry_type = "DYNAMIC_EMA_BOUNCE" if abs(closes[-1] - ema_50) / ema_50 < 0.01 else "PULLBACK_FLIP"
        elif structure == "LH_LL" and ema_50 < ema_200 and rsi_14 <= 55:
            trend = "DOWNTREND"
            entry_type = "PULLBACK_FLIP"
        else:
            trend = "SIDEWAYS"
            entry_type = "WAIT"

        key_support = round(min(lows[-10:]), 4) if len(lows) >= 10 else lows[-1]
        key_resistance = round(max(highs[-10:]), 4) if len(highs) >= 10 else highs[-1]

        return MarketStructureResult(
            trend=trend,
            market_structure=structure,
            ema_50=ema_50,
            ema_200=ema_200,
            rsi_14=rsi_14,
            price_action_pattern=pa_pattern,
            key_support=key_support,
            key_resistance=key_resistance,
            recommended_entry_type=entry_type,
        )
