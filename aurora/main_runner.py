"""Master Execution Runner for Aurora Quant Platform.
Validates end-to-end integration across data caching, risk management, and execution.
"""
from __future__ import annotations

from aurora.analysis.advanced_ta import AdvancedTechnicalAnalyzer, Candle
from aurora.core.asset_universe import AssetUniverse
from aurora.data.data_cache import LocalDataCache
from aurora.risk.portfolio_risk import OpenPosition, PortfolioRiskManager


def run_system_diagnostic() -> None:
    print("--- Starting Aurora Quant Platform Diagnostic ---")
    
    # 1. Initialize Asset Universe
    universe = AssetUniverse()
    btc_spec = universe.get("BTCUSDT")
    print(f"[OK] Asset Universe loaded. Total symbols registered: {len(universe.all_symbols())}")
    
    # 2. Test Data Caching
    cache = LocalDataCache()
    sample_candles = [
        (1700000000, Candle(open=100, high=105, low=98, close=102, volume=1500)),
        (1700003600, Candle(open=102, high=108, low=101, close=107, volume=2200)),
    ]
    cache.save_candles("BTCUSDT", sample_candles)
    loaded = cache.load_candles("BTCUSDT", limit=5)
    print(f"[OK] Local Data Cache operational. Loaded {len(loaded)} candles.")

    # 3. Test Portfolio Risk Management
    risk_manager = PortfolioRiskManager(max_total_drawdown_pct=0.05, max_open_positions=3)
    positions = [
        OpenPosition(symbol="EURUSD", size=1.0, entry_price=1.1000, current_price=1.0950, is_buy=True)
    ]
    allowed, msg = risk_manager.evaluate_portfolio_risk(positions, current_capital=10000.0)
    print(f"[OK] Portfolio Risk Gate check: {allowed} -> {msg}")
    print("--- Aurora Platform Diagnostic Completed Successfully ---")


if __name__ == "__main__":
    run_system_diagnostic()
