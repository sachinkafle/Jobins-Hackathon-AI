"""
Simple in-memory cache manager for AI matching results.
This bypasses fastapi-cache2 which has issues with POST endpoints and Depends() injected parameters.
"""
import time
from typing import Any, Optional

class InMemoryCache:
    def __init__(self):
        self._store: dict = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        self._store[key] = (value, time.time() + ttl_seconds)

    def delete(self, key: str):
        self._store.pop(key, None)

    def clear(self):
        self._store.clear()

# Global singleton cache instance
ai_cache = InMemoryCache()
