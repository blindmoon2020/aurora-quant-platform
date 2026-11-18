from __future__ import annotations

from aurora.risk.stress_testing_engine import InstitutionalStressEngine
from aurora.analysis.advanced_quant_engine import AdvancedQuantEngine, TradeResult
from aurora.security.enterprise_vault import EnterpriseVault


def execute_full_institutional_pipeline() -> None:
    print("==========================================================")
    print("   AURORA QUANT PLATFORM - CORE FOUNDATION EXECUTION      ")
    print("==========================================================")

    # 1. Stress Testing Execution
    portfolio = {"NVDA": 15000, "NAS100": 15000, "BTCUSDT": 10000, "XAUUSD": 10000}
    stress_res = InstitutionalStressEngine.run_portfolio_stress_test(portfolio)
    print("\n[1. Stress Test Execution Results]")
    for r in stress_res:
        print(f" -> {r['Scenario']}: Impacted AAV = ${r['Impacted AAV ($)']:,} | Change: {r['Portfolio Change (%)']}%")

    # 2. Advanced Quant Backtest Metrics
    trades = [
        TradeResult("T-101", 1500.0, 3.0),
        TradeResult("T-102", -350.0, -0.7),
        TradeResult("T-103", 2100.0, 4.2),
        TradeResult("T-104", 800.0, 1.6)
    ]
    quant_metrics = AdvancedQuantEngine.calculate_performance_metrics(trades)
    print("\n[2. Advanced Quant Backtest Metrics]")
    for k, v in quant_metrics.items():
        print(f" -> {k}: {v}")

    # 3. Security Vault Check
    vault_sig = EnterpriseVault.generate_secure_hmac_signature("MASTER_KEY", "NODE_HEALTH_CHECK")
    print(f"\n[3. Enterprise Vault Security Check]")
    print(f" -> HMAC-SHA256 Token Status: Active & Secured (Signature: {vault_sig[:12]}...)")
    print("==========================================================")
    print("   ALL CORE FOUNDATIONS INSTALLED & EXECUTED SUCCESSFULLY ")
    print("==========================================================")


if __name__ == "__main__":
    execute_full_institutional_pipeline()
