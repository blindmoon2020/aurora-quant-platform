import math
from typing import Dict, List, Optional


def compute_portfolio_var(
    aav_capital: float,
    weights: List[float],
    volatilities: List[float],
    confidence_z: float = 1.65,
    correlation_matrix: Optional[List[List[float]]] = None,
) -> float:
    """محاسبه ارزش در معرض خطر (VaR) پارامتریک سبد با پشتیبانی از ماتریس همبستگی."""
    if aav_capital <= 0 or not weights or len(weights) != len(volatilities):
        return 0.0

    n = len(weights)
    if correlation_matrix and len(correlation_matrix) == n and all(len(row) == n for row in correlation_matrix):
        variance = 0.0
        for i in range(n):
            for j in range(n):
                rho = correlation_matrix[i][j]
                variance += weights[i] * weights[j] * volatilities[i] * volatilities[j] * rho
        portfolio_vol = math.sqrt(max(0.0, variance))
    else:
        weighted_var = sum((w * v) ** 2 for w, v in zip(weights, volatilities))
        portfolio_vol = math.sqrt(max(0.0, weighted_var))

    return round(aav_capital * portfolio_vol * max(0.0, confidence_z), 2)


def build_correlation_matrix(symbols: List[str]) -> Dict[str, Dict[str, float]]:
    """ماتریس همبستگی پایه میان دارایی‌های سبد برای جلوگیری از تمرکز پنهان ریسک."""
    matrix: Dict[str, Dict[str, float]] = {}
    for s1 in symbols:
        u1 = s1.upper()
        matrix[s1] = {}
        for s2 in symbols:
            u2 = s2.upper()
            if s1 == s2:
                matrix[s1][s2] = 1.0
            elif ("XAU" in u1 and "USD" in u2) or ("USD" in u1 and "XAU" in u2):
                matrix[s1][s2] = -0.35
            elif ("BRENT" in u1 and "WHEAT" in u2) or ("WHEAT" in u1 and "BRENT" in u2):
                matrix[s1][s2] = 0.25
            else:
                matrix[s1][s2] = 0.15
    return matrix


def align_risk_with_psych_profile(psych_score: int, aav_capital: float) -> dict:
    """تطبیق سقف افت سرمایه، هشدار همگام‌سازی رفتاری و سناریوی ضرر با آزمون روانشناسی."""
    safe_capital = max(0.0, float(aav_capital))
    clamped_score = max(1, min(12, int(psych_score)))

    if clamped_score <= 6:
        profile = "Ultra-Conservative"
        daily_dd_pct = 2.0
        max_dd_pct = 5.0
        herd_guard = "فعال — محدودیت سخت‌گیرانه در برابر نوسانات ناگهانی"
        weights = [0.45, 0.15, 0.25, 0.10, 0.05]
        glass_box_reasoning = "اولویت حفظ سرمایه و کنترل شدید افت روزانه بر اساس پروفایل محافظه‌کارانه."
    elif clamped_score >= 10:
        profile = "Dynamic Alpha"
        daily_dd_pct = 5.0
        max_dd_pct = 12.0
        herd_guard = "فعال — کنترل اهرم و هشدار تمرکز بیش از حد"
        weights = [0.15, 0.25, 0.15, 0.40, 0.05]
        glass_box_reasoning = "تخصیص پویاتر با حفظ سقف‌های تعریف‌شده برای جلوگیری از افت کنترل‌نشده."
    else:
        profile = "Institutional Balanced"
        daily_dd_pct = 3.0
        max_dd_pct = 8.0
        herd_guard = "فعال — تعادل میان حفظ سرمایه و بازده هدف"
        weights = [0.30, 0.20, 0.20, 0.20, 0.10]
        glass_box_reasoning = "توازن نظام‌مند میان نقدشوندگی، طلا/کالا و شاخص‌ها بر اساس پروفایل متعادل."

    vols = [0.012, 0.018, 0.015, 0.020, 0.009]
    var_95 = compute_portfolio_var(safe_capital, weights, vols)
    daily_loss_cap = round(safe_capital * (daily_dd_pct / 100.0), 2)
    max_loss_amount = round(safe_capital * (max_dd_pct / 100.0), 2)

    return {
        "risk_profile": profile,
        "daily_dd_limit_pct": daily_dd_pct,
        "max_dd_limit_pct": max_dd_pct,
        "daily_loss_cap_amount": daily_loss_cap,
        "max_loss_stress_amount": max_loss_amount,
        "var_95": var_95,
        "behavioral_herd_guard": herd_guard,
        "glass_box_reasoning": glass_box_reasoning,
    }
