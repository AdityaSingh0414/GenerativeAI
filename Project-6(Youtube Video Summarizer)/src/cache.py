"""
cache.py
--------
SQLite-backed cache: transcripts keyed by video_id, summaries keyed by
(video_id, config_hash) so changing settings invalidates the cache.
"""

import hashlib
import json
import os
import sqlite3
import time
from contextlib import contextmanager
from typing import Any, Optional


_SCHEMA = """
CREATE TABLE IF NOT EXISTS transcripts (
    video_id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS summaries (
    cache_key TEXT PRIMARY KEY,
    video_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at REAL NOT NULL
);
"""


class Cache:
    def __init__(self, db_path: str):
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self.db_path = db_path
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def get_transcript(self, video_id: str) -> Optional[Any]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT payload FROM transcripts WHERE video_id = ?", (video_id,)
            ).fetchone()
        return json.loads(row[0]) if row else None

    def set_transcript(self, video_id: str, payload: Any) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO transcripts (video_id, payload, created_at) "
                "VALUES (?, ?, ?)",
                (video_id, json.dumps(payload), time.time()),
            )

    @staticmethod
    def make_config_hash(**config) -> str:
        raw = json.dumps(config, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def get_summary(self, video_id: str, config_hash: str) -> Optional[Any]:
        cache_key = f"{video_id}:{config_hash}"
        with self._connect() as conn:
            row = conn.execute(
                "SELECT payload FROM summaries WHERE cache_key = ?", (cache_key,)
            ).fetchone()
        return json.loads(row[0]) if row else None

    def set_summary(self, video_id: str, config_hash: str, payload: Any) -> None:
        cache_key = f"{video_id}:{config_hash}"
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO summaries (cache_key, video_id, payload, created_at) "
                "VALUES (?, ?, ?, ?)",
                (cache_key, video_id, json.dumps(payload), time.time()),
            )

    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM transcripts")
            conn.execute("DELETE FROM summaries")

    def stats(self) -> dict:
        with self._connect() as conn:
            n_transcripts = conn.execute("SELECT COUNT(*) FROM transcripts").fetchone()[0]
            n_summaries = conn.execute("SELECT COUNT(*) FROM summaries").fetchone()[0]
        return {"cached_transcripts": n_transcripts, "cached_summaries": n_summaries}