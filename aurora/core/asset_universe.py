"""Global Multi-Asset & Multi-Exchange Universe Registry (Institutional Edition).

Covers:
1. Global Exchanges & Indices (US, Europe, India, SE Asia, Middle East, Africa, Iran)
2. Equities (Tiered: Liquid Top-100 Blue Chips across Global & Emerging Markets)
3. Forex (Majors, Crosses, and Emerging Markets: INR, ZAR, TRY, BRL, KRW, AED, NGN, AZN, IRR)
4. Metals & Precious Stones (Gold, Silver, Platinum, Palladium, LME Base Metals, Uranium, Lithium, Diamond)
5. Agriculture & Softs (CBOT/ICE Grains, Oilseeds, Coffee, Orange Juice, Livestock, Lumber + IME Saffron, Pistachio, Cumin)
6. Energy (WTI, Brent, Natural Gas, Heating Oil, RBOB Gasoline)
7. Fixed Income & Bonds (US Treasuries 2Y/5Y/10Y/30Y/Ultra, German Bund, JGB, Iran Treasury Bills & Sukuk)
8. ETFs & Mutual Funds (Index, Country-Specific, Sector, Commodity, Vanguard, Fidelity, Iran Gold & Fixed Income Funds)
9. Cryptocurrencies (Layer-1s, DeFi, Stablecoins)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class AssetCategory(str, Enum):
    FOREX = "forex"
    PRECIOUS_METAL_STONE = "precious_metal_stone"
    BASE_BATTERY_METAL = "base_battery_metal"
    ENERGY = "energy"
    AGRICULTURE = "agriculture"
    EQUITY_GLOBAL = "equity_global"
    EQUITY_EMERGING = "equity_emerging"
    EQUITY_IRAN = "equity_iran"
    INDEX = "index"
    BOND_FIXED_INCOME = "bond_fixed_income"
    ETF = "etf"
    MUTUAL_FUND = "mutual_fund"
    CRYPTO = "crypto"


class SubCategory(str, Enum):
    # Forex
    FX_MAJOR = "fx_major"
    FX_CROSS = "fx_cross"
    FX_EMERGING = "fx_emerging"
    # Metals & Stones
    PRECIOUS = "precious"
    GEMSTONE = "gemstone"
    LME_INDUSTRIAL = "lme_industrial"
    BATTERY_NUCLEAR = "battery_nuclear"
    # Agriculture
    GRAINS_OILSEEDS = "grains_oilseeds"
    SOFTS = "softs"
    LIVESTOCK_LUMBER = "livestock_lumber"
    IME_AGRI = "ime_agri"
    # Fixed Income
    SOVEREIGN_FUTURES = "sovereign_futures"
    ISLAMIC_SUKUK_TBILL = "islamic_sukuk_tbill"
    # Funds & ETFs
    ETF_INDEX = "etf_index"
    ETF_COUNTRY = "etf_country"
    ETF_SECTOR_COMMODITY = "etf_sector_commodity"
    FUND_GLOBAL = "fund_global"
    FUND_IRAN = "fund_iran"
    # General
    REGIONAL_INDEX = "regional_index"
    BLUE_CHIP = "blue_chip"
    CRYPTO_SPOT = "crypto_spot"
    ENERGY_FUTURES = "energy_futures"


@dataclass(frozen=True)
class ExchangeInfo:
    code: str
    name: str
    country: str
    region: str
    currency: str
    timezone: str


@dataclass(frozen=True)
class AssetSpec:
    symbol: str
    name: str
    category: AssetCategory
    sub_category: SubCategory
    exchange: str
    region: str
    currency: str
    tick_size: float
    contract_size: float = 1.0
    min_lot: float = 0.01
    margin_rate: float = 1.0
    data_provider: str = "yahoo"
    execution_venue: str = "manual"
    tags: List[str] = field(default_factory=list)


class AssetUniverse:
    """Centralized, searchable registry of global exchanges and multi-asset instruments."""

    def __init__(self) -> None:
        self.exchanges: Dict[str, ExchangeInfo] = {}
        self._assets: Dict[str, AssetSpec] = {}
        self._load_exchanges()
        self._load_full_catalog()

    # ---- Registration & Query API -----------------------------------------
    def register_exchange(self, info: ExchangeInfo) -> None:
        self.exchanges[info.code.upper()] = info

    def register(self, spec: AssetSpec) -> None:
        self._assets[spec.symbol.upper()] = spec

    def get(self, symbol: str) -> Optional[AssetSpec]:
        return self._assets.get(symbol.upper())

    def by_category(self, category: AssetCategory) -> List[AssetSpec]:
        return [a for a in self._assets.values() if a.category == category]

    def by_sub_category(self, sub_category: SubCategory) -> List[AssetSpec]:
        return [a for a in self._assets.values() if a.sub_category == sub_category]

    def by_region(self, region: str) -> List[AssetSpec]:
        r = region.lower()
        return [a for a in self._assets.values() if a.region.lower() == r]

    def by_exchange(self, exchange_code: str) -> List[AssetSpec]:
        ex = exchange_code.upper()
        return [a for a in self._assets.values() if a.exchange.upper() == ex]

    def search_by_tag(self, tag: str) -> List[AssetSpec]:
        t = tag.lower()
        return [a for a in self._assets.values() if t in [x.lower() for x in a.tags]]

    def summary_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for asset in self._assets.values():
            counts[asset.category.value] = counts.get(asset.category.value, 0) + 1
        return counts

    def all_symbols(self) -> List[str]:
        return list(self._assets.keys())

    # ---- Global Exchanges Catalog -----------------------------------------
    def _load_exchanges(self) -> None:
        exchanges = [
            # North America
            ExchangeInfo("NYSE", "New York Stock Exchange", "USA", "North America", "USD", "America/New_York"),
            ExchangeInfo("NASDAQ", "NASDAQ Stock Market", "USA", "North America", "USD", "America/New_York"),
            ExchangeInfo("CME", "Chicago Mercantile Exchange", "USA", "North America", "USD", "America/Chicago"),
            ExchangeInfo("CBOT", "Chicago Board of Trade", "USA", "North America", "USD", "America/Chicago"),
            ExchangeInfo("NYMEX", "New York Mercantile Exchange", "USA", "North America", "USD", "America/New_York"),
            ExchangeInfo("ICE", "Intercontinental Exchange", "USA/UK", "Global", "USD", "America/New_York"),
            ExchangeInfo("TSX", "Toronto Stock Exchange", "Canada", "North America", "CAD", "America/Toronto"),
            # Europe
            ExchangeInfo("LSE", "London Stock Exchange", "UK", "Europe", "GBP", "Europe/London"),
            ExchangeInfo("LME", "London Metal Exchange", "UK", "Europe", "USD", "Europe/London"),
            ExchangeInfo("XETRA", "Deutsche Börse Xetra", "Germany", "Europe", "EUR", "Europe/Berlin"),
            ExchangeInfo("EUREX", "Eurex Derivatives Exchange", "Germany", "Europe", "EUR", "Europe/Berlin"),
            ExchangeInfo("EURONEXT", "Euronext Paris/Amsterdam", "EU", "Europe", "EUR", "Europe/Paris"),
            # Asia-Pacific & India
            ExchangeInfo("NSE", "National Stock Exchange of India", "India", "South Asia", "INR", "Asia/Kolkata"),
            ExchangeInfo("BSE", "Bombay Stock Exchange", "India", "South Asia", "INR", "Asia/Kolkata"),
            ExchangeInfo("TSE", "Tokyo Stock Exchange", "Japan", "East Asia", "JPY", "Asia/Tokyo"),
            ExchangeInfo("HKEX", "Hong Kong Exchanges", "Hong Kong", "East Asia", "HKD", "Asia/Hong_Kong"),
            ExchangeInfo("KRX", "Korea Exchange", "South Korea", "East Asia", "KRW", "Asia/Seoul"),
            ExchangeInfo("SGX", "Singapore Exchange", "Singapore", "SE Asia", "SGD", "Asia/Singapore"),
            ExchangeInfo("IDX", "Indonesia Stock Exchange", "Indonesia", "SE Asia", "IDR", "Asia/Jakarta"),
            ExchangeInfo("SET", "Stock Exchange of Thailand", "Thailand", "SE Asia", "THB", "Asia/Bangkok"),
            ExchangeInfo("ASX", "Australian Securities Exchange", "Australia", "Oceania", "AUD", "Australia/Sydney"),
            # Middle East & Iran
            ExchangeInfo("TSETMC", "Tehran Stock Exchange", "Iran", "Middle East", "IRR", "Asia/Tehran"),
            ExchangeInfo("IME", "Iran Mercantile Exchange", "Iran", "Middle East", "IRR", "Asia/Tehran"),
            ExchangeInfo("IFB", "Iran Fara Bourse", "Iran", "Middle East", "IRR", "Asia/Tehran"),
            ExchangeInfo("TADAWUL", "Saudi Exchange", "Saudi Arabia", "Middle East", "SAR", "Asia/Riyadh"),
            ExchangeInfo("DFM", "Dubai Financial Market", "UAE", "Middle East", "AED", "Asia/Dubai"),
            ExchangeInfo("BIST", "Borsa Istanbul", "Turkey", "Middle East", "TRY", "Europe/Istanbul"),
            # Africa & Latin America
            ExchangeInfo("JSE", "Johannesburg Stock Exchange", "South Africa", "Africa", "ZAR", "Africa/Johannesburg"),
            ExchangeInfo("EGX", "Egyptian Exchange", "Egypt", "Africa", "EGP", "Africa/Cairo"),
            ExchangeInfo("NGX", "Nigerian Exchange Group", "Nigeria", "Africa", "NGN", "Africa/Lagos"),
            ExchangeInfo("B3", "Brasil Bolsa Balcão", "Brazil", "Latin America", "BRL", "America/Sao_Paulo"),
            # OTC & Crypto
            ExchangeInfo("OTC", "Global Interbank FX/Spot", "Global", "Global", "USD", "UTC"),
            ExchangeInfo("BINANCE", "Binance Global Spot/Futures", "Global", "Global", "USDT", "UTC"),
        ]
        for ex in exchanges:
            self.register_exchange(ex)

    # ---- Full Multi-Asset Catalog -----------------------------------------
    def _load_full_catalog(self) -> None:
        items: List[AssetSpec] = [
            # =================================================================
            # 1. GLOBAL INDICES (US, Europe, Asia, India, ME, Africa)
            # =================================================================
            AssetSpec("US30", "Dow Jones Industrial Average", AssetCategory.INDEX, SubCategory.REGIONAL_INDEX, "NYSE", "North America", "USD", 0.1, 1.0, 0.1, 0.02, "mt5", "mt5", ["us", "dow"]),
            AssetSpec("US500", "S&P 500 Index", AssetCategory.INDEX, SubCategory.REGIONAL_INDEX, "CME", "North America", "USD", 0.25, 1.0, 0.1, 0.02, "mt5", "mt5", ["us", "sp500"]),
            AssetSpec("NAS100", "NASDAQ 100 Index", AssetCategory.INDEX, SubCategory.REGIONAL_INDEX, "NASDAQ", "North America", "USD", 0.25, 1.0, 0.1, 0.02, "mt5", "mt5", ["us", "tech", "nasdaq"]),
            AssetSpec("DE40", "DAX 40 Performance Index", AssetCategory.INDEX, SubCategory.REGIONAL_INDEX, "XETRA", "Europe", "EUR", 0.5, 1.0, 0.1, 0.02, "mt5", "mt5", ["germany", "dax"]),
            AssetSpec("UK100", "FTSE 100 Index", AssetCategory.INDEX, SubCategory.REGIONAL_INDEX, "LSE", "Europe", "GBP", 0.5, 1.0, 0.1, 0.02, "mt5", "mt5", ["uk", "ftse"]),
            AssetSpec("FR40", "CAC 40 Index", AssetCategory.INDEX, SubCategory.REGIONAL_INDEX, "EURONEXT", "Europe", "EUR", 0.5, 1.0, 0.1, 0.02, "yahoo", "mt5", ["france", "cac40"]),
            AssetSpec("JP225", "Nikkei 225 Index", AssetCategory.INDEX, SubCategory.REGIONAL_INDEX, "TSE", "East Asia", "JPY", 5.0, 1.0, 0.1, 0.02, "mt5", "mt5", ["japan", "nikkei"]),
            AssetSpec("HK50", "Hang Seng Index", AssetCategory.INDEX, SubCategory.REGIONAL_INDEX, "HKEX", "East Asia", "HKD", 1.0, 1.0, 0.1, 0.02, "mt5", "mt5", ["hongkong", "hsi"]),
            AssetSpec("NIFTY50", "NSE Nifty 50 Index", AssetCategory.INDEX, SubCategory.REGIONAL_INDEX, "NSE", "South Asia", "INR", 0.05, 1.0, 1.0, 0.05, "yahoo", "interactive_brokers", ["india", "nifty"]),
            AssetSpec("SENSEX", "BSE Sensex 30 Index", AssetCategory.INDEX, SubCategory.REGIONAL_INDEX, "BSE", "South Asia", "INR", 0.05, 1.0, 1.0, 0.05, "yahoo", "interactive_brokers", ["india", "sensex"]),
            AssetSpec("STI", "Straits Times Index", AssetCategory.INDEX, SubCategory.REGIONAL_INDEX, "SGX", "SE Asia", "SGD", 0.1, 1.0, 1.0, 0.05, "yahoo", "interactive_brokers", ["singapore", "asean"]),
            AssetSpec("IDX_COMP", "IDX Composite Index", AssetCategory.INDEX, SubCategory.REGIONAL_INDEX, "IDX", "SE Asia", "IDR", 1.0, 1.0, 1.0, 0.1, "yahoo", "interactive_brokers", ["indonesia", "asean"]),
            AssetSpec("TEDPIX", "Tehran Stock Exchange Overall Index", AssetCategory.INDEX, SubCategory.REGIONAL_INDEX, "TSETMC", "Middle East", "IRR", 1.0, 1.0, 1.0, 1.0, "tsetmc", "iran_broker", ["iran", "tedpix"]),
            AssetSpec("TASI", "Tadawul All Share Index", AssetCategory.INDEX, SubCategory.REGIONAL_INDEX, "TADAWUL", "Middle East", "SAR", 0.01, 1.0, 1.0, 0.1, "yahoo", "interactive_brokers", ["saudi", "gcc"]),
            AssetSpec("JTOPI", "FTSE/JSE Top 40 Index", AssetCategory.INDEX, SubCategory.REGIONAL_INDEX, "JSE", "Africa", "ZAR", 1.0, 1.0, 1.0, 0.05, "yahoo", "interactive_brokers", ["south_africa", "africa"]),

            # =================================================================
            # 2. FOREX (Majors, Crosses, Emerging Markets)
            # =================================================================
            # Majors
            AssetSpec("EURUSD", "Euro / US Dollar", AssetCategory.FOREX, SubCategory.FX_MAJOR, "OTC", "Global", "USD", 0.00001, 100000, 0.01, 0.01, "mt5", "mt5", ["major"]),
            AssetSpec("GBPUSD", "British Pound / US Dollar", AssetCategory.FOREX, SubCategory.FX_MAJOR, "OTC", "Global", "USD", 0.00001, 100000, 0.01, 0.01, "mt5", "mt5", ["major"]),
            AssetSpec("USDJPY", "US Dollar / Japanese Yen", AssetCategory.FOREX, SubCategory.FX_MAJOR, "OTC", "Global", "JPY", 0.001, 100000, 0.01, 0.01, "mt5", "mt5", ["major"]),
            AssetSpec("USDCHF", "US Dollar / Swiss Franc", AssetCategory.FOREX, SubCategory.FX_MAJOR, "OTC", "Global", "CHF", 0.00001, 100000, 0.01, 0.01, "mt5", "mt5", ["major"]),
            AssetSpec("USDCAD", "US Dollar / Canadian Dollar", AssetCategory.FOREX, SubCategory.FX_MAJOR, "OTC", "Global", "CAD", 0.00001, 100000, 0.01, 0.01, "mt5", "mt5", ["major"]),
            AssetSpec("AUDUSD", "Australian Dollar / US Dollar", AssetCategory.FOREX, SubCategory.FX_MAJOR, "OTC", "Global", "USD", 0.00001, 100000, 0.01, 0.01, "mt5", "mt5", ["major"]),
            AssetSpec("NZDUSD", "New Zealand Dollar / US Dollar", AssetCategory.FOREX, SubCategory.FX_MAJOR, "OTC", "Global", "USD", 0.00001, 100000, 0.01, 0.01, "mt5", "mt5", ["major"]),
            # Key Crosses
            AssetSpec("EURJPY", "Euro / Japanese Yen", AssetCategory.FOREX, SubCategory.FX_CROSS, "OTC", "Global", "JPY", 0.001, 100000, 0.01, 0.01, "mt5", "mt5", ["cross"]),
            AssetSpec("GBPJPY", "British Pound / Japanese Yen", AssetCategory.FOREX, SubCategory.FX_CROSS, "OTC", "Global", "JPY", 0.001, 100000, 0.01, 0.01, "mt5", "mt5", ["cross"]),
            AssetSpec("EURGBP", "Euro / British Pound", AssetCategory.FOREX, SubCategory.FX_CROSS, "OTC", "Global", "GBP", 0.00001, 100000, 0.01, 0.01, "mt5", "mt5", ["cross"]),
            AssetSpec("AUDCAD", "Australian Dollar / Canadian Dollar", AssetCategory.FOREX, SubCategory.FX_CROSS, "OTC", "Global", "CAD", 0.00001, 100000, 0.01, 0.01, "mt5", "mt5", ["cross"]),
            # Emerging Markets FX (Rupee, Rand, Lira, Real, Won, Dirham, Naira, Manat)
            AssetSpec("USDINR", "US Dollar / Indian Rupee", AssetCategory.FOREX, SubCategory.FX_EMERGING, "OTC", "South Asia", "INR", 0.001, 100000, 0.01, 0.05, "yahoo", "mt5", ["em", "india", "rupee"]),
            AssetSpec("USDZAR", "US Dollar / South African Rand", AssetCategory.FOREX, SubCategory.FX_EMERGING, "OTC", "Africa", "ZAR", 0.0001, 100000, 0.01, 0.05, "mt5", "mt5", ["em", "africa", "rand"]),
            AssetSpec("USDTRY", "US Dollar / Turkish Lira", AssetCategory.FOREX, SubCategory.FX_EMERGING, "OTC", "Middle East", "TRY", 0.0001, 100000, 0.01, 0.05, "mt5", "mt5", ["em", "turkey", "lira"]),
            AssetSpec("USDBRL", "US Dollar / Brazilian Real", AssetCategory.FOREX, SubCategory.FX_EMERGING, "OTC", "Latin America", "BRL", 0.0001, 100000, 0.01, 0.05, "yahoo", "mt5", ["em", "brazil", "real"]),
            AssetSpec("USDKRW", "US Dollar / South Korean Won", AssetCategory.FOREX, SubCategory.FX_EMERGING, "OTC", "East Asia", "KRW", 0.01, 100000, 0.01, 0.05, "yahoo", "mt5", ["em", "korea", "won"]),
            AssetSpec("USDAED", "US Dollar / UAE Dirham", AssetCategory.FOREX, SubCategory.FX_EMERGING, "OTC", "Middle East", "AED", 0.0001, 100000, 0.01, 0.05, "yahoo", "mt5", ["em", "uae", "dirham"]),
            AssetSpec("USDNGN", "US Dollar / Nigerian Naira", AssetCategory.FOREX, SubCategory.FX_EMERGING, "OTC", "Africa", "NGN", 0.01, 100000, 0.01, 0.1, "yahoo", "manual", ["em", "nigeria", "naira"]),
            AssetSpec("USDAZN", "US Dollar / Azerbaijani Manat", AssetCategory.FOREX, SubCategory.FX_EMERGING, "OTC", "Caucasus", "AZN", 0.0001, 100000, 0.01, 0.1, "yahoo", "manual", ["em", "azerbaijan", "manat"]),

            # =================================================================
            # 3. METALS, PRECIOUS STONES & BATTERY/NUCLEAR
            # =================================================================
            AssetSpec("XAUUSD", "Spot Gold", AssetCategory.PRECIOUS_METAL_STONE, SubCategory.PRECIOUS, "OTC", "Global", "USD", 0.01, 100, 0.01, 0.01, "mt5", "mt5", ["gold", "safe_haven"]),
            AssetSpec("XAGUSD", "Spot Silver", AssetCategory.PRECIOUS_METAL_STONE, SubCategory.PRECIOUS, "OTC", "Global", "USD", 0.001, 5000, 0.01, 0.02, "mt5", "mt5", ["silver", "precious"]),
            AssetSpec("XPTUSD", "Spot Platinum", AssetCategory.PRECIOUS_METAL_STONE, SubCategory.PRECIOUS, "NYMEX", "Global", "USD", 0.1, 50, 0.01, 0.02, "mt5", "mt5", ["platinum", "pgm"]),
            AssetSpec("XPDUSD", "Spot Palladium", AssetCategory.PRECIOUS_METAL_STONE, SubCategory.PRECIOUS, "NYMEX", "Global", "USD", 0.1, 100, 0.01, 0.03, "mt5", "mt5", ["palladium", "pgm"]),
            AssetSpec("DIAMOND_IDX", "Polished Diamond Index / Rough Carat", AssetCategory.PRECIOUS_METAL_STONE, SubCategory.GEMSTONE, "OTC", "Global", "USD", 1.0, 1.0, 1.0, 0.2, "custom_feed", "manual", ["diamond", "gemstone"]),
            # LME Industrial & Battery Metals
            AssetSpec("COPPER", "High Grade Copper", AssetCategory.BASE_BATTERY_METAL, SubCategory.LME_INDUSTRIAL, "LME", "Global", "USD", 0.0005, 25000, 0.01, 0.03, "yahoo", "mt5", ["copper", "lme"]),
            AssetSpec("ALUMINUM", "LME Primary Aluminium", AssetCategory.BASE_BATTERY_METAL, SubCategory.LME_INDUSTRIAL, "LME", "Global", "USD", 0.5, 25, 0.1, 0.05, "yahoo", "interactive_brokers", ["aluminum", "lme"]),
            AssetSpec("NICKEL", "LME Primary Nickel", AssetCategory.BASE_BATTERY_METAL, SubCategory.LME_INDUSTRIAL, "LME", "Global", "USD", 5.0, 6, 0.1, 0.05, "yahoo", "interactive_brokers", ["nickel", "lme", "ev"]),
            AssetSpec("ZINC", "LME Special High Grade Zinc", AssetCategory.BASE_BATTERY_METAL, SubCategory.LME_INDUSTRIAL, "LME", "Global", "USD", 0.5, 25, 0.1, 0.05, "yahoo", "interactive_brokers", ["zinc", "lme"]),
            AssetSpec("LEAD", "LME Standard Lead", AssetCategory.BASE_BATTERY_METAL, SubCategory.LME_INDUSTRIAL, "LME", "Global", "USD", 0.5, 25, 0.1, 0.05, "yahoo", "interactive_brokers", ["lead", "lme"]),
            AssetSpec("TIN", "LME Refined Tin", AssetCategory.BASE_BATTERY_METAL, SubCategory.LME_INDUSTRIAL, "LME", "Global", "USD", 5.0, 5, 0.1, 0.05, "yahoo", "interactive_brokers", ["tin", "lme"]),
            AssetSpec("IRON_ORE", "SGX TSI Iron Ore 62% Fe", AssetCategory.BASE_BATTERY_METAL, SubCategory.LME_INDUSTRIAL, "SGX", "Asia", "USD", 0.05, 100, 0.1, 0.05, "yahoo", "interactive_brokers", ["iron_ore", "steel"]),
            AssetSpec("URANIUM", "U3O8 Uranium Futures", AssetCategory.BASE_BATTERY_METAL, SubCategory.BATTERY_NUCLEAR, "NYMEX", "Global", "USD", 0.05, 250, 0.1, 0.1, "yahoo", "interactive_brokers", ["uranium", "nuclear"]),
            AssetSpec("LITHIUM", "Lithium Hydroxide CIF CJK", AssetCategory.BASE_BATTERY_METAL, SubCategory.BATTERY_NUCLEAR, "CME", "Global", "USD", 0.01, 1000, 0.1, 0.1, "yahoo", "interactive_brokers", ["lithium", "battery", "ev"]),

            # =================================================================
            # 4. ENERGY
            # =================================================================
            AssetSpec("WTI", "Crude Oil WTI", AssetCategory.ENERGY, SubCategory.ENERGY_FUTURES, "NYMEX", "Global", "USD", 0.01, 100, 0.01, 0.02, "mt5", "mt5", ["oil", "wti"]),
            AssetSpec("BRENT", "Brent Crude Oil", AssetCategory.ENERGY, SubCategory.ENERGY_FUTURES, "ICE", "Global", "USD", 0.01, 100, 0.01, 0.02, "mt5", "mt5", ["oil", "brent"]),
            AssetSpec("NATGAS", "Henry Hub Natural Gas", AssetCategory.ENERGY, SubCategory.ENERGY_FUTURES, "NYMEX", "Global", "USD", 0.001, 1000, 0.01, 0.05, "mt5", "mt5", ["gas", "natgas"]),

            # =================================================================
            # 5. AGRICULTURE (Global CBOT/ICE + Iran Mercantile Exchange IME)
            # =================================================================
            AssetSpec("ZW_WHEAT", "Chicago SRW Wheat", AssetCategory.AGRICULTURE, SubCategory.GRAINS_OILSEEDS, "CBOT", "Global", "USD", 0.25, 50, 0.1, 0.05, "yahoo", "mt5", ["wheat", "grain"]),
            AssetSpec("KE_WHEAT", "Kansas HRW Wheat", AssetCategory.AGRICULTURE, SubCategory.GRAINS_OILSEEDS, "CBOT", "Global", "USD", 0.25, 50, 0.1, 0.05, "yahoo", "interactive_brokers", ["kansas_wheat", "grain"]),
            AssetSpec("ZS_SOYBEAN", "Soybeans Futures", AssetCategory.AGRICULTURE, SubCategory.GRAINS_OILSEEDS, "CBOT", "Global", "USD", 0.25, 50, 0.1, 0.05, "yahoo", "mt5", ["soybean"]),
            AssetSpec("ZM_SOYMEAL", "Soybean Meal Futures", AssetCategory.AGRICULTURE, SubCategory.GRAINS_OILSEEDS, "CBOT", "Global", "USD", 0.1, 100, 0.1, 0.05, "yahoo", "interactive_brokers", ["soymeal"]),
            AssetSpec("ZL_SOYOIL", "Soybean Oil Futures", AssetCategory.AGRICULTURE, SubCategory.GRAINS_OILSEEDS, "CBOT", "Global", "USD", 0.01, 600, 0.1, 0.05, "yahoo", "interactive_brokers", ["soyoil"]),
            AssetSpec("ZR_RICE", "Rough Rice Futures", AssetCategory.AGRICULTURE, SubCategory.GRAINS_OILSEEDS, "CBOT", "Global", "USD", 0.005, 2000, 0.1, 0.05, "yahoo", "interactive_brokers", ["rice"]),
            AssetSpec("ZO_OATS", "Oats Futures", AssetCategory.AGRICULTURE, SubCategory.GRAINS_OILSEEDS, "CBOT", "Global", "USD", 0.25, 50, 0.1, 0.05, "yahoo", "interactive_brokers", ["oats"]),
            AssetSpec("RS_CANOLA", "ICE Canola Futures", AssetCategory.AGRICULTURE, SubCategory.GRAINS_OILSEEDS, "ICE", "North America", "CAD", 0.1, 20, 0.1, 0.05, "yahoo", "interactive_brokers", ["canola"]),
            AssetSpec("KC_ARABICA", "Coffee C Arabica", AssetCategory.AGRICULTURE, SubCategory.SOFTS, "ICE", "Global", "USD", 0.05, 375, 0.1, 0.05, "yahoo", "mt5", ["coffee", "arabica"]),
            AssetSpec("RC_ROBUSTA", "Robusta Coffee Futures", AssetCategory.AGRICULTURE, SubCategory.SOFTS, "ICE", "Europe", "USD", 1.0, 10, 0.1, 0.05, "yahoo", "interactive_brokers", ["coffee", "robusta"]),
            AssetSpec("OJ_ORANGE", "Frozen Concentrated Orange Juice", AssetCategory.AGRICULTURE, SubCategory.SOFTS, "ICE", "Global", "USD", 0.05, 150, 0.1, 0.05, "yahoo", "interactive_brokers", ["orange_juice"]),
            AssetSpec("LE_CATTLE", "Live Cattle Futures", AssetCategory.AGRICULTURE, SubCategory.LIVESTOCK_LUMBER, "CME", "North America", "USD", 0.025, 400, 0.1, 0.05, "yahoo", "interactive_brokers", ["livestock", "cattle"]),
            AssetSpec("LBR_LUMBER", "Random Length Lumber", AssetCategory.AGRICULTURE, SubCategory.LIVESTOCK_LUMBER, "CME", "North America", "USD", 0.5, 27.5, 0.1, 0.05, "yahoo", "interactive_brokers", ["lumber"]),
            # Iran Mercantile Exchange (IME) Strategic Agri
            AssetSpec("SAFFRON_IME", "IME Negin Saffron Futures/CD", AssetCategory.AGRICULTURE, SubCategory.IME_AGRI, "IME", "Iran", "IRR", 100.0, 1.0, 1.0, 0.2, "tsetmc", "iran_broker", ["saffron", "iran", "ime"]),
            AssetSpec("PISTACHIO_IME", "IME Pistachio Certificate of Deposit", AssetCategory.AGRICULTURE, SubCategory.IME_AGRI, "IME", "Iran", "IRR", 100.0, 1.0, 1.0, 1.0, "tsetmc", "iran_broker", ["pistachio", "iran", "ime"]),
            AssetSpec("CUMIN_IME", "IME Green Cumin Certificate", AssetCategory.AGRICULTURE, SubCategory.IME_AGRI, "IME", "Iran", "IRR", 100.0, 1.0, 1.0, 1.0, "tsetmc", "iran_broker", ["cumin", "iran", "ime"]),

            # =================================================================
            # 6. BONDS & FIXED INCOME (US, EU, Japan, Iran)
            # =================================================================
            AssetSpec("ZT_2Y", "US 2-Year T-Note Futures", AssetCategory.BOND_FIXED_INCOME, SubCategory.SOVEREIGN_FUTURES, "CBOT", "North America", "USD", 0.0078125, 2000, 0.1, 0.02, "yahoo", "interactive_brokers", ["bond", "us2y"]),
            AssetSpec("ZF_5Y", "US 5-Year T-Note Futures", AssetCategory.BOND_FIXED_INCOME, SubCategory.SOVEREIGN_FUTURES, "CBOT", "North America", "USD", 0.0078125, 1000, 0.1, 0.02, "yahoo", "interactive_brokers", ["bond", "us5y"]),
            AssetSpec("ZN_10Y", "US 10-Year T-Note Futures", AssetCategory.BOND_FIXED_INCOME, SubCategory.SOVEREIGN_FUTURES, "CBOT", "North America", "USD", 0.015625, 1000, 0.1, 0.02, "yahoo", "interactive_brokers", ["bond", "us10y"]),
            AssetSpec("ZB_30Y", "US 30-Year T-Bond Futures", AssetCategory.BOND_FIXED_INCOME, SubCategory.SOVEREIGN_FUTURES, "CBOT", "North America", "USD", 0.03125, 1000, 0.1, 0.02, "yahoo", "interactive_brokers", ["bond", "us30y"]),
            AssetSpec("UB_ULTRA", "US Ultra T-Bond Futures", AssetCategory.BOND_FIXED_INCOME, SubCategory.SOVEREIGN_FUTURES, "CBOT", "North America", "USD", 0.03125, 1000, 0.1, 0.02, "yahoo", "interactive_brokers", ["bond", "ultra"]),
            AssetSpec("FGBL_BUND", "Euro-Bund 10Y German Bond", AssetCategory.BOND_FIXED_INCOME, SubCategory.SOVEREIGN_FUTURES, "EUREX", "Europe", "EUR", 0.01, 1000, 0.1, 0.02, "yahoo", "interactive_brokers", ["bond", "germany", "bund"]),
            AssetSpec("FGBM_BOBL", "Euro-Bobl 5Y German Bond", AssetCategory.BOND_FIXED_INCOME, SubCategory.SOVEREIGN_FUTURES, "EUREX", "Europe", "EUR", 0.01, 1000, 0.1, 0.02, "yahoo", "interactive_brokers", ["bond", "germany", "bobl"]),
            AssetSpec("JGB_10Y", "10-Year Japanese Gov Bond", AssetCategory.BOND_FIXED_INCOME, SubCategory.SOVEREIGN_FUTURES, "TSE", "East Asia", "JPY", 0.01, 1000000, 0.1, 0.02, "yahoo", "interactive_brokers", ["bond", "japan", "jgb"]),
            AssetSpec("AKHAZA_IR", "Iran Islamic Treasury Bills (Akhaza)", AssetCategory.BOND_FIXED_INCOME, SubCategory.ISLAMIC_SUKUK_TBILL, "IFB", "Iran", "IRR", 1.0, 1.0, 1.0, 1.0, "tsetmc", "iran_broker", ["tbill", "iran", "fixed_income"]),
            AssetSpec("SUKUK_IJARA", "Iran Corporate Ijara Sukuk", AssetCategory.BOND_FIXED_INCOME, SubCategory.ISLAMIC_SUKUK_TBILL, "IFB", "Iran", "IRR", 1.0, 1.0, 1.0, 1.0, "tsetmc", "iran_broker", ["sukuk", "iran", "fixed_income"]),

            # =================================================================
            # 7. GLOBAL & EMERGING EQUITIES (Tiered Liquid Leaders)
            # =================================================================
            AssetSpec("NVDA", "NVIDIA Corp", AssetCategory.EQUITY_GLOBAL, SubCategory.BLUE_CHIP, "NASDAQ", "North America", "USD", 0.01, 1.0, 1.0, 0.5, "yahoo", "alpaca", ["us", "ai"]),
            AssetSpec("AAPL", "Apple Inc", AssetCategory.EQUITY_GLOBAL, SubCategory.BLUE_CHIP, "NASDAQ", "North America", "USD", 0.01, 1.0, 1.0, 0.5, "yahoo", "alpaca", ["us", "tech"]),
            AssetSpec("SAP", "SAP SE", AssetCategory.EQUITY_GLOBAL, SubCategory.BLUE_CHIP, "XETRA", "Europe", "EUR", 0.01, 1.0, 1.0, 0.5, "yahoo", "interactive_brokers", ["europe", "germany"]),
            AssetSpec("RELIANCE", "Reliance Industries Ltd", AssetCategory.EQUITY_EMERGING, SubCategory.BLUE_CHIP, "NSE", "South Asia", "INR", 0.05, 1.0, 1.0, 0.5, "yahoo", "interactive_brokers", ["india", "nifty50"]),
            AssetSpec("TCS", "Tata Consultancy Services", AssetCategory.EQUITY_EMERGING, SubCategory.BLUE_CHIP, "NSE", "South Asia", "INR", 0.05, 1.0, 1.0, 0.5, "yahoo", "interactive_brokers", ["india", "it"]),
            AssetSpec("DBS", "DBS Group Holdings", AssetCategory.EQUITY_EMERGING, SubCategory.BLUE_CHIP, "SGX", "SE Asia", "SGD", 0.01, 1.0, 1.0, 0.5, "yahoo", "interactive_brokers", ["singapore", "asean"]),
            AssetSpec("BBCA", "Bank Central Asia Tbk", AssetCategory.EQUITY_EMERGING, SubCategory.BLUE_CHIP, "IDX", "SE Asia", "IDR", 25.0, 100.0, 1.0, 1.0, "yahoo", "interactive_brokers", ["indonesia", "asean"]),
            AssetSpec("NPN", "Naspers Ltd", AssetCategory.EQUITY_EMERGING, SubCategory.BLUE_CHIP, "JSE", "Africa", "ZAR", 1.0, 1.0, 1.0, 0.5, "yahoo", "interactive_brokers", ["south_africa", "africa"]),
            AssetSpec("ARAMCO", "Saudi Arabian Oil Co", AssetCategory.EQUITY_EMERGING, SubCategory.BLUE_CHIP, "TADAWUL", "Middle East", "SAR", 0.05, 1.0, 1.0, 1.0, "yahoo", "interactive_brokers", ["saudi", "oil"]),
            AssetSpec("FOOLAD", "Mobarakeh Steel Co", AssetCategory.EQUITY_IRAN, SubCategory.BLUE_CHIP, "TSETMC", "Iran", "IRR", 1.0, 1.0, 1.0, 1.0, "tsetmc", "iran_broker", ["iran", "steel"]),
            AssetSpec("FEMELI", "National Iranian Copper Ind.", AssetCategory.EQUITY_IRAN, SubCategory.BLUE_CHIP, "TSETMC", "Iran", "IRR", 1.0, 1.0, 1.0, 1.0, "tsetmc", "iran_broker", ["iran", "copper"]),

            # =================================================================
            # 8. ETFs & MUTUAL FUNDS (Global, Country, Commodity, Vanguard, Iran)
            # =================================================================
            # Index & Commodity ETFs
            AssetSpec("SPY", "SPDR S&P 500 ETF Trust", AssetCategory.ETF, SubCategory.ETF_INDEX, "NYSE", "North America", "USD", 0.01, 1.0, 1.0, 0.5, "yahoo", "alpaca", ["etf", "index"]),
            AssetSpec("GLD", "SPDR Gold Shares ETF", AssetCategory.ETF, SubCategory.ETF_SECTOR_COMMODITY, "NYSE", "Global", "USD", 0.01, 1.0, 1.0, 0.5, "yahoo", "alpaca", ["etf", "gold"]),
            AssetSpec("SLV", "iShares Silver Trust ETF", AssetCategory.ETF, SubCategory.ETF_SECTOR_COMMODITY, "NYSE", "Global", "USD", 0.01, 1.0, 1.0, 0.5, "yahoo", "alpaca", ["etf", "silver"]),
            # Country ETFs (India, Japan, Brazil, Turkey, Egypt, Saudi Arabia)
            AssetSpec("INDA", "iShares MSCI India ETF", AssetCategory.ETF, SubCategory.ETF_COUNTRY, "NYSE", "South Asia", "USD", 0.01, 1.0, 1.0, 0.5, "yahoo", "alpaca", ["etf", "india"]),
            AssetSpec("EWJ", "iShares MSCI Japan ETF", AssetCategory.ETF, SubCategory.ETF_COUNTRY, "NYSE", "East Asia", "USD", 0.01, 1.0, 1.0, 0.5, "yahoo", "alpaca", ["etf", "japan"]),
            AssetSpec("EWZ", "iShares MSCI Brazil ETF", AssetCategory.ETF, SubCategory.ETF_COUNTRY, "NYSE", "Latin America", "USD", 0.01, 1.0, 1.0, 0.5, "yahoo", "alpaca", ["etf", "brazil"]),
            AssetSpec("TUR", "iShares MSCI Turkey ETF", AssetCategory.ETF, SubCategory.ETF_COUNTRY, "NASDAQ", "Middle East", "USD", 0.01, 1.0, 1.0, 0.5, "yahoo", "alpaca", ["etf", "turkey"]),
            AssetSpec("EGPT", "VanEck Egypt Index ETF", AssetCategory.ETF, SubCategory.ETF_COUNTRY, "NYSE", "Africa", "USD", 0.01, 1.0, 1.0, 0.5, "yahoo", "alpaca", ["etf", "egypt", "africa"]),
            AssetSpec("KSA", "iShares MSCI Saudi Arabia ETF", AssetCategory.ETF, SubCategory.ETF_COUNTRY, "NYSE", "Middle East", "USD", 0.01, 1.0, 1.0, 0.5, "yahoo", "alpaca", ["etf", "saudi"]),
            # Mutual Funds (Vanguard, Fidelity, Iran ETFs/Funds)
            AssetSpec("VTI", "Vanguard Total Stock Market", AssetCategory.MUTUAL_FUND, SubCategory.FUND_GLOBAL, "NYSE", "North America", "USD", 0.01, 1.0, 1.0, 1.0, "yahoo", "alpaca", ["vanguard", "total_market"]),
            AssetSpec("VOO", "Vanguard S&P 500 Index Fund", AssetCategory.MUTUAL_FUND, SubCategory.FUND_GLOBAL, "NYSE", "North America", "USD", 0.01, 1.0, 1.0, 1.0, "yahoo", "alpaca", ["vanguard", "sp500"]),
            AssetSpec("VXUS", "Vanguard Total International Stock", AssetCategory.MUTUAL_FUND, SubCategory.FUND_GLOBAL, "NASDAQ", "Global", "USD", 0.01, 1.0, 1.0, 1.0, "yahoo", "alpaca", ["vanguard", "international"]),
            AssetSpec("BND", "Vanguard Total Bond Market", AssetCategory.MUTUAL_FUND, SubCategory.FUND_GLOBAL, "NASDAQ", "North America", "USD", 0.01, 1.0, 1.0, 1.0, "yahoo", "alpaca", ["vanguard", "bond"]),
            AssetSpec("VWNDX", "Vanguard Windsor Fund", AssetCategory.MUTUAL_FUND, SubCategory.FUND_GLOBAL, "NASDAQ", "North America", "USD", 0.01, 1.0, 1.0, 1.0, "yahoo", "interactive_brokers", ["vanguard", "windsor"]),
            AssetSpec("FXAIX", "Fidelity 500 Index Fund", AssetCategory.MUTUAL_FUND, SubCategory.FUND_GLOBAL, "NASDAQ", "North America", "USD", 0.01, 1.0, 1.0, 1.0, "yahoo", "interactive_brokers", ["fidelity", "sp500"]),
            AssetSpec("AYAR", "Mofid Gold Bullion ETF", AssetCategory.MUTUAL_FUND, SubCategory.FUND_IRAN, "TSETMC", "Iran", "IRR", 1.0, 1.0, 1.0, 1.0, "tsetmc", "iran_broker", ["iran", "gold_etf"]),
            AssetSpec("KAMAND", "Kamand Fixed Income ETF", AssetCategory.MUTUAL_FUND, SubCategory.FUND_IRAN, "IFB", "Iran", "IRR", 1.0, 1.0, 1.0, 1.0, "tsetmc", "iran_broker", ["iran", "fixed_income"]),

            # =================================================================
            # 9. CRYPTOCURRENCIES
            # =================================================================
            AssetSpec("BTCUSDT", "Bitcoin / Tether", AssetCategory.CRYPTO, SubCategory.CRYPTO_SPOT, "BINANCE", "Global", "USDT", 0.01, 1.0, 0.001, 0.1, "ccxt", "ccxt", ["crypto", "btc"]),
            AssetSpec("ETHUSDT", "Ethereum / Tether", AssetCategory.CRYPTO, SubCategory.CRYPTO_SPOT, "BINANCE", "Global", "USDT", 0.01, 1.0, 0.01, 0.1, "ccxt", "ccxt", ["crypto", "eth"]),
            AssetSpec("SOLUSDT", "Solana / Tether", AssetCategory.CRYPTO, SubCategory.CRYPTO_SPOT, "BINANCE", "Global", "USDT", 0.01, 1.0, 0.1, 0.1, "ccxt", "ccxt", ["crypto", "sol"]),
            AssetSpec("XAU_PAXG", "PAX Gold Tokenized Gold", AssetCategory.CRYPTO, SubCategory.CRYPTO_SPOT, "BINANCE", "Global", "USDT", 0.1, 1.0, 0.01, 0.2, "ccxt", "ccxt", ["crypto", "gold"]),
        ]
        for item in items:
            self.register(item)
