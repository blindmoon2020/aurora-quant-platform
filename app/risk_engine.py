import math
from typing import List, Dict


def compute_portfolio_var(aav_capital: float, weights: List[float], volatilities: List[float], confidence_z: float = 1.65) -> float:
    """محاسبه تقریبی ارزش در معرض خطر (VaR) پارامتریک سبد."""
    if aav_capital <= 0 or not weights or len(weights) != len(volatilities):
        return 0.0
    weighted_var = sum((w * v) ** 2 for w, v in zip(weights, volatilities))
    portfolio_vol = math.sqrt(max(0.0, weighted_var))
    return round(aav_capital * portfolio_vol * confidence_z, 2)


def build_correlation_matrix(symbols: List[str]) -> Dict[str, Dict[str, float]]:
    """ماتریس همبستگی پایه میان دارایی‌های سبد برای جلوگیری از تمرکز پنهان ریسک."""
    matrix: Dict[str, Dict[str, float]] = {}
    for s1 in symbols:
        matrix[s1] = {}
        for s2 in symbols:
            if s1 == s2:
                matrix[s1][s2] = 1.0
            elif ("XAU" in s1 and "USD" in s2) or ("USD" in s1 and "XAU" in s2):
                matrix[s1][s2] = -0.35
            elif ("BRENT" in s1 and "WHEAT" in s2) or ("WHEAT" in s1 and "BRENT" in s2):
                matrix[s1][s2] = 0.25
            else:
                matrix[s1][s2] = 0.15
    return matrix


def align_risk_with_psych_profile(psych_score: int, aav_capital: float) -> dict:
    """تطبیق سقف افت سرمایه، هشدار همگام‌سازی رفتاری و سناریوی ضرر با آزمون روانشناسی."""
    if psych_score <= 6:
        profile = "Ultra-Conservative"
        daily_dd_pct = 2.0
        max_dd_pct = 5.0
        herd_guard = "فعال — محدودیت سخت‌گیرانه در برابر نوسانات ناگهانی"
        weights = [0.45, 0.15, 0.25, 0.10, 0.05]
    elif psych_score >= 10:
        profile = "Dynamic Alpha"
        daily_dd_pct = 5.0
        max_dd_pct = 12.0
        herd_guard = "فعال — کنترل اهرم و هشدار تمرکز بیش از حد"
        weights = [0.15, 0.25, 0.15, 0.40, 0.05]
    else:
        profile = "Institutional Balanced"
        daily_dd_pct = 3.0
        max_dd_pct = 8.0
        herd_guard = "فعال — تعادل میان حفظ سرمایه و بازده هدف"
        weights = [0.30, 0.20, 0.20, 0.20, 0.10]

    vols = [0.012, 0.018, 0.015, 0.020, 0.009]
    var_95 = compute_portfolio_var(aav_capital, weights, vols)
    max_loss_amount = round(aav_capital * (max_dd_pct / 100.0), 2)

    return {
        "risk_profile": profile,
        "daily_dd_limit_pct": daily_dd_pct,
        "max_dd_limit_pct": max_dd_pct,
        "max_loss_stress_amount": max_loss_amount,
        "var_95": var_95,
        "behavioral_herd_guard": herd_guard,
    }
