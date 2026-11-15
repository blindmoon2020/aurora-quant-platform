"""Automated AI Report Generator for Aurora Platform.
Synthesizes SMC technicals, fundamental sentiment, and intermarket data into client-ready reports.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional
from aurora.analysis.smart_money_quant import SMCAnalysisResult
from aurora.analysis.intermarket_correlation import IntermarketState


@dataclass(frozen=True)
class ClientMarketReport:
    symbol: str
    headline: str
    executive_summary: str
    technical_outlook: str
    risk_warning: str
    llm_prompt_payload: str


class AIReportGenerator:
    """Transforms raw quantitative indicators into clear, human-readable client reports."""

    def generate_report(
        self,
        symbol: str,
        current_price: float,
        smc_result: SMCAnalysisResult,
        intermarket_state: IntermarketState,
        sentiment_score: float,
    ) -> ClientMarketReport:
        sym = symbol.upper()
        
        # 1. Construct dynamic headline based on SMC structure
        if "BULLISH" in smc_result.market_structure:
            headline = f"تحلیل بازار {sym}: ساختار صعودی و تاییدیه هوشمند اسمارت مانی"
        elif "BEARISH" in smc_result.market_structure:
            headline = f"تحلیل بازار {sym}: فشار عرضه و ساختار نزولی حاکم بر بازار"
        else:
            headline = f"تحلیل بازار {sym}: وضعیت رنج و نوسان در محدوده تعادلی"

        # 2. Executive Summary
        summary = (
            f"قیمت کنونی {sym} در سطح ${current_price:,.2f} قرار دارد. "
            f"وضعیت همبستگی با شاخص دلار (DXY) در حالت '{intermarket_state.market_regime}' بوده و "
            f"امتیاز احساسات فاندامنتال خبری {sentiment_score:+.2f} ارزیابی شده است."
        )

        # 3. Technical Outlook
        tech_desc = (
            f"بر اساس الگوریتم اسمارت مانی (SMC)، ساختار بازار در حالت {smc_result.market_structure} است. "
            f"نقطه کنترل حجمی (POC) در محدوده ${smc_result.volume_poc:,.2f} و سطح کلیدی فیبوناچی ۰.۶۱۸ در ${smc_result.fib_retracement_618:,.2f} شناسایی شد. "
            f"وجود نقدینگی جاروب‌شده (Liquidity Sweep): {smc_result.liquidity_sweep}."
        )

        # 4. Risk Warning
        risk_text = (
            "هشدار مدیریت ریسک: بازارهای مالی دارای ریسک ذاتی هستند. "
            "پیشنهاد می‌شود حداکثر ۱ تا ۳ درصد سرمایه در هر معامله درگیر شده و حد ضرر پشت آخرین ساختار معتبر رعایت شود."
        )

        # 5. Raw Payload for LLM API (OpenAI / Claude)
        prompt_payload = f"""
[System Prompt for LLM Client Report Generation]
Role: Senior Financial Investment Analyst at Aurora Wealth.
Task: Write a polished, professional, and easy-to-understand market analysis report for retail and institutional clients in Persian.
Data Inputs:
- Symbol: {sym}
- Price: {current_price}
- Market Structure: {smc_result.market_structure}
- DXY Correlation: {intermarket_state.correlation_with_dxy}
- Sentiment: {sentiment_score}
- Rationale: {smc_result.rationale}
"""

        return ClientMarketReport(
            symbol=sym,
            headline=headline,
            executive_summary=summary,
            technical_outlook=tech_desc,
            risk_warning=risk_text,
            llm_prompt_payload=prompt_payload.strip(),
        )
