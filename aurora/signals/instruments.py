"""Global Instruments & Commodities Registry for Aurora Quant Core.
Covers Global Indices, Precious/Industrial Metals, Energy/Petrochemicals, and Agribusiness (Coffee, Wheat, Saffron).
"""
from __future__ import annotations
from typing import Dict, List, Any

GLOBAL_INSTRUMENTS_DB: Dict[str, Dict[str, Any]] = {
    "METALS": {
        "XAUUSD": {"name": "Gold Spot", "exchange": "FOREX/COMEX", "provider": "TwelveData/MetaTrader"},
        "XAGUSD": {"name": "Silver Spot", "exchange": "FOREX/COMEX", "provider": "TwelveData"},
        "COPPER": {"name": "Copper Futures", "exchange": "LME/COMEX", "provider": "TwelveData"}
    },
    "ENERGY_PETROCHEMICALS": {
        "BRENT": {"name": "Brent Crude Oil", "exchange": "ICE", "provider": "TwelveData"},
        "WTI": {"name": "WTI Crude Oil", "exchange": "NYMEX", "provider": "TwelveData"},
        "NATGAS": {"name": "Natural Gas", "exchange": "NYMEX", "provider": "TwelveData"},
        "POLYMER": {"name": "Petrochemicals / Polymers Index", "exchange": "ICIS/Global", "provider": "Custom Feed"}
    },
    "AGRIBUSINESS_COMMODITIES": {
        "WHEAT": {"name": "Wheat Futures", "exchange": "CBOT", "provider": "TwelveData"},
        "COFFEE": {"name": "Coffee Arabica", "exchange": "ICE", "provider": "TwelveData"},
        "SAFFRON": {"name": "Global Saffron Index (Saffron Spot)", "exchange": "Middle East/Global", "provider": "Custom Commodity Feed"}
    },
    "INDICES": {
        "US30": {"name": "Dow Jones Industrial Average", "exchange": "NYSE", "provider": "Tiingo/Bloomberg"},
        "NAS100": {"name": "Nasdaq 100", "exchange": "NASDAQ", "provider": "Tiingo/Bloomberg"},
        "SPX": {"name": "S&P 500", "exchange": "CBOE", "provider": "Tiingo/Bloomberg"}
    }
}

class InstrumentRegistry:
    @staticmethod
    def get_all_symbols() -> List[str]:
        symbols = []
        for category in GLOBAL_INSTRUMENTS_DB.values():
            symbols.extend(category.keys())
        return symbols

    @staticmethod
    def get_instrument_meta(symbol: str) -> Dict[str, Any]:
        for category in GLOBAL_INSTRUMENTS_DB.values():
            if symbol in category:
                return category[symbol]
        return {"name": symbol, "exchange": "Unknown", "provider": "Generic"}
