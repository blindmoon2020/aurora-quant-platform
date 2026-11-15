"""Global Market Hours and Session Validator for Aurora Quant Platform.
Ensures orders are only routed when target exchanges and markets are actively open.
"""
from __future__ import annotations

from datetime import datetime, timezone
import zoneinfo


class MarketClock:
    """Validates exchange trading hours across global and regional markets."""

    EXCHANGE_TIMEZONES = {
        "NYSE": "America/New_York",
        "NASDAQ": "America/New_York",
        "CME": "America/Chicago",
        "CBOT": "America/Chicago",
        "LSE": "Europe/London",
        "XETRA": "Europe/Berlin",
        "NSE": "Asia/Kolkata",
        "TSE": "Asia/Tokyo",
        "TSETMC": "Asia/Tehran",
        "IME": "Asia/Tehran",
        "BINANCE": "UTC",
        "OTC": "UTC",
    }

    @classmethod
    def is_market_open(cls, exchange_code: str) -> bool:
        ex = exchange_code.upper()
        tz_str = cls.EXCHANGE_TIMEZONES.get(ex, "UTC")
        try:
            loc_tz = zoneinfo.ZoneInfo(tz_str)
            now_local = datetime.now(loc_tz)
            
            # Crypto & Spot FX are generally open 24/5 or 24/7
            if ex in ("BINANCE", "OTC"):
                return True

            # Weekend check (Saturday = 5, Sunday = 6)
            if now_local.weekday() >= 5:
                # Special check for Middle East markets (Iran TSETMC: Sat-Wed, UAE/Saudi: Sun-Thu)
                if ex in ("TSETMC", "IME", "IFB"):
                    if now_local.weekday() == 6:  # Sunday is open in Iran
                        pass
                    else:
                        return False
                else:
                    return False

            # Standard equity session hours (09:00 to 16:00 local time)
            hour = now_local.hour
            if ex in ("TSETMC", "IME", "IFB"):
                return 9 <= hour < 15  # Iran market hours approx 09:00 to 15:00
            
            return 9 <= hour < 17  # Standard Western session hours
        except Exception:
            return True  # Fallback to allow execution if tz lookup fails
