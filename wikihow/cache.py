"""
WikiHow Article Cache
======================
Simple file-based JSON cache with TTL expiration.
Caches API responses in ~/.wikihow/cache/ to avoid redundant requests.
"""

import hashlib
import json
import os
import time
from pathlib import Path

CACHE_DIR = Path.home() / ".wikihow" / "cache"
DEFAULT_TTL = 3600  # 1 hour in seconds


def _ensure_cache_dir():
    """Create cache directory if it doesn't exist."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_key(key: str) -> str:
    """Generate a filesystem-safe cache filename from a key."""
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:32] + ".json"


def get(key: str, ttl: int = DEFAULT_TTL) -> dict | None:
    """
    Retrieve a cached value if it exists and hasn't expired.

    Args:
        key: Cache key (e.g. article title or search query)
        ttl: Time-to-live in seconds

    Returns:
        Cached dict or None if miss/expired
    """
    _ensure_cache_dir()
    path = CACHE_DIR / _cache_key(key)

    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            entry = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    # Check expiration
    cached_at = entry.get("_cached_at", 0)
    if time.time() - cached_at > ttl:
        path.unlink(missing_ok=True)
        return None

    return entry.get("data")


def put(key: str, data: dict):
    """
    Store a value in the cache.

    Args:
        key: Cache key
        data: Dict to cache
    """
    _ensure_cache_dir()
    path = CACHE_DIR / _cache_key(key)

    entry = {
        "_cached_at": time.time(),
        "data": data,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False)


def clear():
    """Remove all cached files."""
    if CACHE_DIR.exists():
        for f in CACHE_DIR.iterdir():
            if f.suffix == ".json":
                f.unlink(missing_ok=True)
