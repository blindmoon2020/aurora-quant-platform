"""Institutional Smart Money Concepts (SMC), Volume Profile, Market Structure,
Liquidity Sweeps, and Auto-Fibonacci Engine for Aurora Platform.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from aurora.analysis.advanced_ta import Candle


@dataclass(frozen=True)
class SMCAnalysisResult:
    market_structure: str          # "BOS_BULLISH", "BOS_BEARISH", "CHOCH_BULLISH", "CHOCH_BEARISH", "RANGING"
    liquidity_sweep: bool          # True if price grabbed external liquidity highs/lows
    smart_money_trap: bool         # True if retail breakout trap detected
    supply_zone: Tuple[float, float]     # (Zone High, Zone Low)
    demand_zone: Tuple[float, float]    # (Zone High, Zone Low)
    volume_poc: float              # Point of Control (Volume Profile max node)
    fib_retracement_618: float     # Golden Ratio 0.618 level
    rationale: List[str] = field(default_factory=list)


class SmartMoneyQuantEngine:
    """Advanced institutional price action and liquidity analytics engine."""

    @staticmethod
    def calculate_volume_profile_poc(candles: List[Candle]) -> float:
        """Calculates approximate Point of Control (POC) using volume distribution across price bins."""
        if not candles:
            return 0.0
        
        lows = [c.low for c in candles]
        highs = [c.high for c in candles]
        min_p, max_p = min(lows), max(highs)
        if min_p == max_p:
            return min_p

        bins = 10
        step = (max_p - min_p) / bins
        bin_volumes = [0.0] * bins

        for c in candles:
            avg_price = (c.high + c.low + c.close) / 3.0
            idx = min(bins - 1, int((avg_price - min_p) / step)) if step > 0 else 0
            bin_volumes[idx] += c.volume

        max_vol_idx = bin_volumes.index(max(bin_volumes))
        poc = min_p + (max_vol_idx + 0.5) * step
        return round(poc, 4)

    @staticmethod
    def detect_smc_structure(candles: List[Candle]) -> SMCAnalysisResult:
        """Detects BOS, CHoCH, Liquidity Sweeps, SM Traps, Supply/Demand, and Fibs."""
        if len(candles) < 10:
            return SMCAnalysisResult(
                market_structure="RANGING",
                liquidity_sweep=False,
                smart_money_trap=False,
                supply_zone=(0.0, 0.0),
                demand_zone=(0.0, 0.0),
                volume_poc=0.0,
                fib_retracement_618=0.0,
                rationale=["Insufficient candles for SMC analysis."],
            )

        closes = [c.close for c in candles]
        highs = [c.high for c in candles]
        lows = [c.low for c in candles]

        recent_high = max(highs[-10:-1])
        recent_low = min(lows[-10:-1])
        current_candle = candles[-1]

        rationale = []
        structure = "RANGING"
        liq_sweep = False
        sm_trap = False

        # 1. Liquidity Grab & Trap Detection
        if current_candle.high > recent_high and current_candle.close < recent_high:
            liq_sweep = True
            sm_trap = True
            rationale.append("Liquidity Sweep & Smart Money Trap detected above key external highs (Retail breakout failure).")
        elif current_candle.low < recent_low and current_candle.close > recent_low:
            liq_sweep = True
            sm_trap = True
            rationale.append("Liquidity Sweep & Smart Money Trap detected below key external lows (Sell-stop purge).")

        # 2. BOS & CHoCH Logic
        if current_candle.close > recent_high and not liq_sweep:
            structure = "CHOCH_BULLISH" if closes[-5] < recent_low else "BOS_BULLISH"
            rationale.append(f"Market Structure Shift: {structure} confirmed with momentum close.")
        elif current_candle.close < recent_low and not liq_sweep:
            structure = "CHOCH_BEARISH" if closes[-5] > recent_high else "BOS_BEARISH"
            rationale.append(f"Market Structure Shift: {structure} confirmed with momentum close.")
        else:
            rationale.append("Market structure consolidating within institutional dealing range.")

        # 3. Supply & Demand Zones
        supply_zone = (round(max(highs[-5:]), 4), round(sum(highs[-5:]) / 5 * 0.995, 4))
        demand_zone = (round(sum(lows[-5:]) / 5 * 1.005, 4), round(min(lows[-5:]), 4))

        # 4. Volume Profile POC
        poc = SmartMoneyQuantEngine.calculate_volume_profile_poc(candles)

        # 5. Auto Fibonacci Retracement (Swing Low to Swing High of last 20 candles)
        swing_low = min(lows[-20:]) if len(lows) >= 20 else min(lows)
        swing_high = max(highs[-20:]) if len(highs) >= 20 else max(highs)
        diff = swing_high - swing_low
        fib_618 = round(swing_high - (diff * 0.618), 4)

        return SMCAnalysisResult(
            market_structure=structure,
            liquidity_sweep=liq_sweep,
            smart_money_trap=sm_trap,
            supply_zone=supply_zone,
            demand_zone=demand_zone,
            volume_poc=poc,
            fib_retracement_618=fib_618,
            rationale=rationale,
        )
