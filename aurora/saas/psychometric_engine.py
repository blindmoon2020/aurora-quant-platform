"""Sensitive Behavioral Finance & Psychometric Risk Profiling Engine.
Includes weighted scoring, emotional drawdown sensitivity, and contradiction detection.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class RiskAssessmentReport:
    raw_score: int               # 4 to 40
    normalized_score: int      # 1 to 10
    profile_category: str      # "CONSERVATIVE", "BALANCED", "GROWTH", "AGGRESSIVE"
    contradiction_detected: bool
    behavioral_warning: str
    max_allowed_drawdown_pct: float


class PsychometricRiskEngine:
    """Evaluates investor psychology with weighted sensitivity and consistency checks."""

    QUESTIONS = [
        {
            "id": "Q1_HORIZON",
            "text": "افق زمانی سرمایه‌گذاری شما چقدر است؟",
            "weight": 1.0,
            "options": {1: "کمتر از ۱ سال", 3: "۱ تا ۳ سال", 6: "۳ تا ۵ سال", 10: "بیش از ۵ سال"},
        },
        {
            "id": "Q2_DRAWDOWN_REACTION",
            "text": "اگر سبد شما در یک ماه ۱۵٪ افت کند، واکنش شما چیست؟",
            "weight": 1.5,  # Highest psychological sensitivity weight
            "options": {1: "فروش کامل و خروج", 4: "فروش بخشی از سبد", 7: "حفظ سبد و صبر", 10: "خرید بیشتر در کف"},
        },
        {
            "id": "Q3_GOAL",
            "text": "هدف اصلی شما از سرمایه‌گذاری چیست؟",
            "weight": 1.2,
            "options": {2: "حفظ ارزش پول در برابر تورم", 5: "رشد پایدار و کم‌نوسان", 8: "رشد بالا", 10: "حداکثر بازدهی و اهرم"},
        },
        {
            "id": "Q4_EXPERIENCE",
            "text": "میزان تجربه و دانش شما در بازارهای مالی چقدر است؟",
            "weight": 1.1,
            "options": {1: "بدون تجربه", 4: "مبتدی (صندوق/سپرده)", 7: "متوسط (سهام/طلا)", 10: "حرفه‌ای و
