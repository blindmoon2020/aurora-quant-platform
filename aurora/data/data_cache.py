"""Local High-Performance Data Caching & Persistence Engine for Aurora Platform.
Stores candle histories and market feeds locally to eliminate network latency.
"""
from __future__ import annotations

import json
import sqlite3
from typing import List, Optional
from aurora.analysis.advanced_ta import Candle


class LocalDataCache:
    """SQLite-backed persistent cache for market candles and asset pricing."""

    def __init__(self, db_path: str = "aurora_market_data.db") -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS candles_cache (
                    symbol TEXT,
                    timestamp INTEGER,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume REAL,
                    PRIMARY KEY (symbol, timestamp)
                )
                """
            )
            conn.commit()

    def save_candles(self, symbol: str, candles: List[tuple[int, Candle]]) -> None:
        """Saves a batch of timestamped candles to local persistent storage."""
        sym = symbol.upper()
        with sqlite3.connect(self.db_path) as conn:
            data = [
                (sym, ts, c.open, c.high, c.low, c.close, c.volume)
                for ts, c in candles
            ]
            conn.executemany(
                """
                INSERT OR REPLACE INTO candles_cache (symbol, timestamp, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                data,
            )
            conn.commit()

    def load_candles(self, symbol: str, limit: int = 200) -> List[Candle]:
        """Loads cached candles ordered by timestamp descending/ascending."""
        sym = symbol.upper()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor(
                "SELECT open, high, low, close, volume FROM candles_cache WHERE symbol = ? ORDER BY timestamp ASC LIMIT ?",
                (sym, limit),
            )
            rows = cursor.fetchall() if hasattr(cursor, 'fetchall') else conn.execute(
                "SELECT open, high, low, close, volume FROM candles_cache WHERE symbol = ? ORDER BY timestamp ASC LIMIT ?",
                (sym, limit),
            ).fetchall()

        return [
            Candle(open=r[0], high=r[1], low=r[2], close=r[3], volume=r[4])
            for r in rows
        ]
