"""Institutional Psychometric Risk Profiling Engine (CFA Standard).
Evaluates investor risk tolerance and capacity to compute optimal asset weights.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

@dataclass
class InvestorProfile:
    tolerance_score: int  # 1 to 10
    time_horizon_years: int
    objective: str        # 'preservation', 'growth', 'alpha'

class InstitutionalPsychometricEngine:
    @staticmethod
    def evaluate_profile(profile: InvestorProfile) -> Dict[str, float]:
        """Calculates dynamic asset allocation weights based on psychological metrics."""
        if profile.objective == "preservation" or profile.tolerance_score <= 4:
            # Conservative
            return {"NVDA": 0.15, "NAS100": 0.15, "BTCUSDT": 0.05, "XAUUSD": 0.65}
        elif profile.objective == "alpha" or profile.tolerance_score >= 8:
            # Aggressive Alpha
            return {"NVDA": 0.45, "NAS100": 0.35, "BTCUSDT": 0.15, "XAUUSD": 0.05}
        else:
            # Balanced Institutional
            return {"NVDA": 0.30, "NAS100": 0.30, "BTCUSDT": 0.20, "XAUUSD": 0.20}
