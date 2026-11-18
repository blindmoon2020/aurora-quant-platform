"""Enterprise Stress Testing & Macro Shock Engine for Aurora Quant Platform.
Inspired by BlackRock Aladdin & MSCI Barra risk management frameworks.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class StressScenario:
    scenario_name: str
    market_shock_pct: float
    gold_impact_pct: float
    crypto_impact_pct: float


class InstitutionalStressEngine:
    @staticmethod
    def run_portfolio_stress_test(portfolio_assets: Dict[str, float]) -> List[Dict[str, float | str]]:
        """Applies severe market shocks (e.g., liquidity crisis, geopolitical spike)
        to evaluate portfolio resilience and Maximum Drawdown (MDD).
        """
        scenarios = [
            StressScenario("Global Liquidity Crunch", -0.15, 0.08, -0.25),
            StressScenario("Geopolitical Gold & Oil Spike", -0.05, 0.12, -0.10),
            StressScenario("Systemic Tech Sell-off", -0.22, 0.05, -0.30)
        ]
        
        results = []
        total_value = sum(portfolio_assets.values())

        for sc in scenarios:
            simulated_loss = 0.0
            for asset, val in portfolio_assets.items():
                if "NVDA" in asset or "NAS100" in asset:
                    simulated_loss += val * sc.market_shock_pct
                elif "XAUUSD" in asset:
                    simulated_loss += val * sc.gold_impact_pct
                elif "BTC" in asset:
                    simulated_loss += val * sc.crypto_impact_pct

            new_aav = total_value + simulated_loss
            pct_change = (simulated_loss / total_value) * 100

            results.append({
                "Scenario": sc.scenario_name,
                "Impacted AAV ($)": round(new_aav, 2),
                "Portfolio Change (%)": round(pct_change, 2)
            })

        return results


if __name__ == "__main__":
    print("[INFO] Initializing Aurora Institutional Stress Testing Engine...")
    sample_portfolio = {"NVDA": 15000, "NAS100": 15000, "BTCUSDT": 10000, "XAUUSD": 10000}
    stress_results = InstitutionalStressEngine.run_portfolio_stress_test(sample_portfolio)
    for res in stress_results:
        print(f" -> {res['Scenario']}: New AAV = ${res['Impacted AAV ($)']:,} ({res['Portfolio Change (%)']}% )")
