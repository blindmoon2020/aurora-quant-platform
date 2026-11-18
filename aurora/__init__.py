"""Aurora v2: Institutional Quant & Wealth Management Core.
Integrated modular architecture preserving all legacy risk and execution layers.
"""
__version__ = "0.1.0"

try:
    from aurora import backtest_runner
    from aurora.risk import stress_testing_engine
except ImportError:
    pass
