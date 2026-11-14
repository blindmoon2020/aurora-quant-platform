"""Macroeconomic Calendar (Forex Factory Feed), Fundamental RSS News Aggregator,
and TradingView Webhook Signal Receiver.
"""
from __future__ import annotations

import json
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class EconomicEvent:
    title: str
    country: str          # e.g., USD, EUR, GBP, JPY, CNY
    impact: str           # High, Medium, Low, Holiday
    timestamp_utc: int    # Unix epoch in seconds
    forecast: str = ""
    previous: str = ""


@dataclass(frozen=True)
class NewsHeadline:
    title: str
    source: str
    published_utc: int
    sentiment_score: float   # -1.0 (Bearish) to +1.0 (Bullish)
    related_tags: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class TradingViewAlert:
    symbol: str
    action: str           # BUY, SELL, EXIT
    price: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    strategy_name: str
    timeframe: str
    ts: int


class MacroNewsHub:
    """Connects Aurora to Forex Factory calendar feeds, RSS news, and TradingView webhooks."""

    FF_WEEKLY_XML_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"

    BULLISH_KEYWORDS = {
        "surge", "rally", "growth", "beat", "expansion", "hawkish",
        "demand", "stimulus", "record high", "upgrade", "profit",
    }
    BEARISH_KEYWORDS = {
        "crash", "recession", "inflation", "miss", "contraction", "dovish",
        "sanction", "war", "default", "downgrade", "slump", "cut",
    }

    def __init__(self) -> None:
        self.events: List[EconomicEvent] = []
        self.headlines: List[NewsHeadline] = []

    # ---- 1. Forex Factory Live Economic Calendar --------------------------
    def fetch_forex_factory_calendar(self, timeout: int = 10) -> List[EconomicEvent]:
        """Fetches and parses the official weekly Forex Factory XML feed."""
        req = urllib.request.Request(
            self.FF_WEEKLY_XML_URL,
            headers={"User-Agent": "AuroraQuantPlatform/2.0"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            xml_bytes = resp.read()

        root = ET.fromstring(xml_bytes)
        parsed: List[EconomicEvent] = []
        for item in root.findall("event"):
            title = (item.findtext("title") or "").strip()
            country = (item.findtext("country") or "").strip().upper()
            impact = (item.findtext("impact") or "Low").strip()
            date_str = (item.findtext("date") or "").strip()
            time_str = (item.findtext("time") or "").strip()
            forecast = (item.findtext("forecast") or "").strip()
            previous = (item.findtext("previous") or "").strip()

            ts = self._parse_ff_datetime(date_str, time_str)
            if ts is not None:
                parsed.append(
                    EconomicEvent(
                        title=title,
                        country=country,
                        impact=impact,
                        timestamp_utc=ts,
                        forecast=forecast,
                        previous=previous,
                    )
                )
        self.events = parsed
        return parsed

    @staticmethod
    def _parse_ff_datetime(date_str: str, time_str: str) -> Optional[int]:
        if not date_str or not time_str or "day" in time_str.lower() or "tentative" in time_str.lower():
            return None
        try:
            dt = datetime.strptime(f"{date_str} {time_str}", "%m-%d-%Y %I:%M%p")
            return int(dt.replace(tzinfo=timezone.utc).timestamp())
        except ValueError:
            return None

    def active_news_lockout(
        self,
        currencies: List[str],
        now_utc: Optional[int] = None,
        window_minutes: int = 30,
    ) -> Optional[str]:
        """Returns a lockout reason if a High-Impact news event is within +/- window_minutes."""
        now = now_utc if now_utc is not None else int(datetime.now(timezone.utc).timestamp())
        window_sec = window_minutes * 60
        target_ccys = {c.upper() for c in currencies}

        for ev in self.events:
            if ev.impact.lower() != "high":
                continue
            if ev.country in target_ccys or "ALL" in target_ccys:
                if abs(ev.timestamp_utc - now) <= window_sec:
                    return f"High-impact {ev.country} event: {ev.title}"
        return None

    # ---- 2. Fundamental News & Sentiment Scorer ---------------------------
    def score_headline_sentiment(self, text: str) -> float:
        """Rule-based institutional financial lexicon sentiment scorer in [-1.0, +1.0]."""
        words = {w.strip(".,!?:;\"'()").lower() for w in text.split()}
        bull_hits = len(words & self.BULLISH_KEYWORDS)
        bear_hits = len(words & self.BEARISH_KEYWORDS)
        total = bull_hits + bear_hits
        if total == 0:
            return 0.0
        return round((bull_hits - bear_hits) / total, 3)

    def ingest_rss_feed(self, rss_url: str, source_name: str, tags: Optional[List[str]] = None, timeout: int = 10) -> List[NewsHeadline]:
        """Reads any standard financial RSS feed (Reuters, Bloomberg, IME, Codal) and scores headlines."""
        req = urllib.request.Request(rss_url, headers={"User-Agent": "AuroraQuantPlatform/2.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            xml_bytes = resp.read()

        root = ET.fromstring(xml_bytes)
        now = int(datetime.now(timezone.utc).timestamp())
        new_items: List[NewsHeadline] = []
        for item in root.findall(".//item")[:25]:
            title = (item.findtext("title") or "").strip()
            if not title:
                continue
            score = self.score_headline_sentiment(title)
            headline = NewsHeadline(
                title=title,
                source=source_name,
                published_utc=now,
                sentiment_score=score,
                related_tags=tags or [],
            )
            new_items.append(headline)
            self.headlines.append(headline)
        return new_items

    def aggregate_sentiment(self, tag: Optional[str] = None) -> float:
        """Computes average fundamental sentiment across stored headlines."""
        relevant = [
            h.sentiment_score
            for h in self.headlines
            if tag is None or tag.lower() in [t.lower() for t in h.related_tags]
        ]
        if not relevant:
            return 0.0
        return round(sum(relevant) / len(relevant), 3)

    # ---- 3. TradingView Webhook Signal Receiver ---------------------------
    @staticmethod
    def parse_tradingview_webhook(payload: str | Dict[str, Any]) -> TradingViewAlert:
        """Parses incoming JSON alerts from TradingView PineScript strategies."""
        data = json.loads(payload) if isinstance(payload, str) else payload
        return TradingViewAlert(
            symbol=str(data["symbol"]).upper(),
            action=str(data["action"]).upper(),
            price=float(data["price"]),
            stop_loss=float(data["stop_loss"]) if data.get("stop_loss") is not None else None,
            take_profit=float(data["take_profit"]) if data.get("take_profit") is not None else None,
            strategy_name=str(data.get("strategy", "TradingView_Pine")),
            timeframe=str(data.get("timeframe", "1H")),
            ts=int(data.get("ts", datetime.now(timezone.utc).timestamp())),
        )
