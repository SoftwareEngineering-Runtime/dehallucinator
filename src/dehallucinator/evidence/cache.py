"""SQLite cache for Wikipedia pages (FR-2.6)."""

import json
import sqlite3
import time
from contextlib import closing
from pathlib import Path

from dehallucinator.config import CACHE_TTL_DAYS

CACHE_PATH = Path(__file__).resolve().parents[3] / "data" / "wiki_cache.sqlite3"
_TTL_SECONDS = CACHE_TTL_DAYS * 24 * 60 * 60


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS pages ("
        "title TEXT PRIMARY KEY, page TEXT NOT NULL, fetched_at REAL NOT NULL)"
    )
    return conn


def get_cached_page(title: str, path: Path = CACHE_PATH, now: float | None = None) -> dict | None:
    """Return the cached page, or None if missing, expired or unreadable."""
    now = time.time() if now is None else now
    try:
        with closing(_connect(path)) as conn:
            row = conn.execute(
                "SELECT page, fetched_at FROM pages WHERE title = ?", (title,)
            ).fetchone()
    except sqlite3.Error:
        return None
    if row is None or now - row[1] > _TTL_SECONDS:
        return None
    return json.loads(row[0])


def put_cached_page(
    title: str, page: dict, path: Path = CACHE_PATH, now: float | None = None
) -> None:
    """Store a page. Cache problems never break retrieval."""
    now = time.time() if now is None else now
    try:
        with closing(_connect(path)) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO pages (title, page, fetched_at) VALUES (?, ?, ?)",
                (title, json.dumps(page), now),
            )
            conn.commit()
    except sqlite3.Error:
        pass
