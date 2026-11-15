# AURORA Quant Platform (`aurora-quant-platform`)

Enterprise Quantitative Investment, Risk Management & Algorithmic Execution Platform.

> **وضعیت واقعی:** پیش از اتکا به این فهرست، `docs/REALITY_CHECK.md` را بخوانید.
> هر ردیف آن با اجرای تست تأیید شده و موارد نبودِ کد صریحاً نام برده شده است.

## Architecture Modules
- `config/`: Risk limits, broker settings, and strategy DNA configurations.
- `core/`: Zero-dependency risk engine, portfolio allocator, and base strategy classes.
- `strategies/`: Pre-registered quantitative trading strategies.
- `backtest/`: Historical simulation harness and Monte Carlo stress testing.
- `execution/`: Universal broker bridges (MT5, Crypto, TSETMC, Manual).
- `analytics/`: Performance metrics (Sharpe, Sortino, Drawdown) and audit reports.
- `api/`: REST/WebSocket interface for multi-account management and investor dashboard.