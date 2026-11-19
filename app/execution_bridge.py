from typing import Dict, List, Optional


SAFE_EXECUTION_POLICIES: Dict[str, object] = {
    "allow_withdrawal": False,
    "require_2fa": True,
    "require_anti_phishing": True,
    "require_psych_lock": True,
    "max_single_order_pct_of_aav": 10.0,
}


def mask_reference_id(raw_value: str, keep_tail: int = 4) -> str:
    """ماسک‌سازی شناسه حساب یا مرجع اتصال برای جلوگیری از افشای داده حساس."""
    cleaned = "".join(ch for ch in str(raw_value or "").strip() if not ch.isspace())
    if not cleaned:
        return "****"
    if len(cleaned) <= keep_tail:
        return "*" * len(cleaned)
    return ("*" * (len(cleaned) - keep_tail)) + cleaned[-keep_tail:]


def evaluate_execution_readiness(
    client_name: str,
    aav_capital: float,
    risk_profile: str,
    is_psych_locked: bool,
    two_fa_enabled: bool,
    anti_phishing_enabled: bool,
    daily_dd_limit_pct: float,
    max_dd_limit_pct: float,
    linked_accounts_count: int,
) -> dict:
    """ارزیابی انطباق، امنیت و آمادگی اجرایی پیش از هرگونه اقدام عملیاتی یا بازتوزیع."""
    blockers: List[str] = []
    warnings: List[str] = []

    if not is_psych_locked:
        blockers.append("آزمون روانشناسی و پروفایل ریسک در هسته قفل نشده است.")
    if not two_fa_enabled:
        blockers.append("تایید دو مرحله‌ای (2FA) فعال نیست.")
    if not anti_phishing_enabled:
        warnings.append("کد آنتی‌فیشینگ فعال نیست؛ فعال‌سازی آن توصیه می‌شود.")
    if aav_capital <= 0:
        blockers.append("سرمایه فعال (AAV) معتبر نیست.")
    if linked_accounts_count <= 0:
        warnings.append("هنوز هیچ حساب متصل و تاییدشده‌ای ثبت نشده است.")

    max_order_cap_amount = round(
        max(0.0, float(aav_capital)) * (float(SAFE_EXECUTION_POLICIES["max_single_order_pct_of_aav"]) / 100.0),
        2,
    )
    daily_loss_guard_amount = round(max(0.0, float(aav_capital)) * (float(daily_dd_limit_pct) / 100.0), 2)
    max_loss_guard_amount = round(max(0.0, float(aav_capital)) * (float(max_dd_limit_pct) / 100.0), 2)

    return {
        "client_name": client_name,
        "ready_for_controlled_execution": len(blockers) == 0,
        "risk_profile": risk_profile,
        "security_controls": {
            "two_fa_enabled": bool(two_fa_enabled),
            "anti_phishing_enabled": bool(anti_phishing_enabled),
            "psych_locked": bool(is_psych_locked),
            "withdrawal_blocked_by_policy": True,
        },
        "risk_guards": {
            "daily_dd_limit_pct": daily_dd_limit_pct,
            "max_dd_limit_pct": max_dd_limit_pct,
            "daily_loss_guard_amount": daily_loss_guard_amount,
            "max_loss_guard_amount": max_loss_guard_amount,
            "max_single_order_cap_amount": max_order_cap_amount,
        },
        "linked_accounts_count": int(linked_accounts_count),
        "blockers": blockers,
        "warnings": warnings,
    }
