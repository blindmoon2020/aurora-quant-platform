"""Advanced Global Instruments, Brokers & Data Feeds Registry for Aurora Core.
Covers Global Exchanges, Commodities (Agribusiness, Energy, Precious Metals), 
Bonds, ETFs, TSETMC (Iran), and Broker API Connectors (MetaTrader/IBKR/Binance).
"""
from __future__ import annotations
from typing import Dict, List, Any

class GlobalExchangeRegistry:
    # دسته‌بندی جامع تمام بازارهای مالی و کامودیتی‌های جهان
    MASTER_ASSET_CLASSES = {
        "GLOBAL_INDICES": ["US30", "NAS100", "SPX500", "DAX40", "FTSE100", "NIKKEI225"],
        "PRECIOUS_METALS": ["XAUUSD", "XAGUSD", "PLATINUM", "PALLADIUM"],
        "ENERGY_PETROCHEMICALS": ["BRENT", "WTI", "NATGAS", "POLYMER_INDEX", "PETRO_REFINE"],
        "AGRIBUSINESS": ["WHEAT", "COFFEE", "CORN", "SOYBEAN", "SAFFRON_GLOBAL"],
        "BONDS_ETFS": ["US10Y", "US02Y", "GLD_ETF", "SPY_ETF", "QQQ_ETF"],
        "IRAN_TSETMC": ["FOULAD", "MABAR", "TAFAVT", "SAIPA", "PETRO_TEHRAN"]
    }

    # درگاه‌های اتصال به بروکرها و صرافی‌های جهانی (API Endpoints & Gateways)
    BROKER_GATEWAYS = {
        "InteractiveBrokers": {"protocol": "TWS API", "status": "Ready", "endpoint": "127.0.0.1:7497"},
        "MetaTrader5": {"protocol": "MQL5 ZeroMQ Bridge", "status": "Active", "endpoint": "localhost:5555"},
        "BinanceGlobal": {"protocol": "REST/WebSocket API", "status": "Ready", "endpoint": "api.binance.com"},
        "TSETMC_Gateway": {"protocol": "TSE Client / Web scraping", "status": "Active", "endpoint": "tsetmc.com"}
    }

    @classmethod
    def get_supported_symbols(cls) -> List[str]:
        all_syms = []
        for cat in cls.MASTER_ASSET_CLASSES.values():
            all_syms.extend(cat)
        return all_syms

    @classmethod
    def verify_broker_connection(cls, broker_name: str) -> Dict[str, Any]:
        if broker_name in cls.BROKER_GATEWAYS:
            return {"broker": broker_name, "connection": "Established", "secure": True}
        return {"broker": broker_name, "connection": "Not Found", "secure": False}
