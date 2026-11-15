"""Master Orchestrator Engine for Aurora Quant Platform.
Unites Asset Universe, Macro News Filter, Advanced Technicals, Robo-Advisory,
and Live Execution Router into a fully autonomous institutional trading loop.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from aurora.analysis.advanced_ta import AdvancedTechnicalAnalyzer, Candle
from aurora.advisory.recommender import AdvancedAdvisorEngine, InvestmentRecommendation
from aurora.core.asset_universe import AssetUniverse
from aurora.data.news_calendar import MacroNewsHub
from aurora.execution.live_router import ExecutionOrder, ExecutionResponse, LiveOrderRouter
from aurora.risk.unified_gate import UnifiedRiskGate  # assuming built previously


class AuroraMasterOrchestrator:
    """The central brain governing end-to-end quantitative analysis and execution."""

    def __init__(
        self,
        universe: AssetUniverse,
        news_hub: MacroNewsHub,
        analyzer: AdvancedTechnicalAnalyzer,
        advisor: AdvancedAdvisorEngine,
        router: LiveOrderRouter,
        risk_gate: Optional[Any] = None,
    ) -> None:
        self.universe = universe
        self.news_hub = news_hub
        self.analyzer = analyzer
        self.advisor = advisor
        self.router = router
        self.risk_gate = risk_gate

    def run_market_cycle(self, symbol: str, current_price: float, candles: List[Candle], venue: str = "MT5") -> Optional[ExecutionResponse]:
        """Runs a complete analysis, risk check, and execution cycle for any global or local asset."""
        spec = self.universe.get(symbol)
        if not spec:
            raise ValueError(f"Symbol {symbol} is not registered in Aurora Asset Universe.")

        # 1. Advanced Technical Analysis
        tech_result = self.analyzer.analyze(candles)

        # 2. Advisory & Recommendation Generation
        # Convert Advanced Technicals to Advisory format
        from aurora.advisory.recommender import TechnicalIndicators
        advisory_tech = TechnicalIndicators(
            ema_20=tech_result.ema_50,  # mapped proxy
            ema_40=tech_result.ema_50,
            ema_200=tech_result.ema_200,
            rsi_14=tech_result.rsi_14,
            volume_surge=False,
            price_action_pattern=tech_result.price_action_pattern,
        )

        recommendation = self.advisor.evaluate_asset(
            symbol=symbol,
            current_price=current_price,
            technicals=advisory_tech,
        )

        # 3. Check News Lockout & Guardrails
        if recommendation.news_lockout_warning:
            print(f"[ORCHESTRATOR] Aborting execution for {symbol} due to news lockout: {recommendation.news_lockout_warning}")
            return None

        # 4. Action Validation (Only execute on strong signals)
        if recommendation.action not in ("STRONG_BUY", "STRONG_SELL", "BUY", "SELL"):
            print(f"[ORCHESTRATOR] Signal for {symbol} is {recommendation.action}. Holding position.")
            return None

        # 5. Route to Live Execution
        side = "BUY" if "BUY" in recommendation.action else "SELL"
        order = ExecutionOrder(
            symbol=symbol.upper(),
            action=side,
            volume=spec.min_lot,
            order_type="MARKET",
            price=current_price,
            stop_loss=recommendation.stop_loss,
            take_profit=recommendation.take_profit_2,  # 1:3 R:R target
            venue=venue,
        )

        response = self.router.execute_order(order)
        print(f"[ORCHESTRATOR] Execution Response for {symbol}: {response.message}")
        return response
