"""In-process memory cache"""

from __future__ import annotations

import time
from threading import RLock
from typing import Any, Dict, Optional


class L1MemoryCache:
    """Thread-safe in-process cache with TTL + LRU eviction"""

    def __init__(
        self,
        max_size: int = 10_000,
        ttl_seconds: int = 3600,
    ):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds

        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = RLock()

    def get(self, key: str) -> Any:
        """Get from cache"""

        if not key:
            return None

        now = time.time()

        with self._lock:
            item = self._cache.get(key)

            if item is None:
                return None

            if item["expires_at"] < now:
                self._cache.pop(key, None)
                return None

            item["last_accessed"] = now
            item["hits"] += 1

            return item["value"]

    def put(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """Store value in cache"""

        if not key:
            raise ValueError("key cannot be empty")

        ttl = ttl_seconds or self.ttl_seconds
        now = time.time()

        with self._lock:
            if len(self._cache) >= self.max_size:
                self._evict_lru()

            self._cache[key] = {
                "value": value,
                "created_at": now,
                "last_accessed": now,
                "expires_at": now + ttl,
                "hits": 0,
            }

    def delete(self, key: str) -> bool:
        """Delete cache entry"""

        with self._lock:
            return self._cache.pop(key, None) is not None

    def exists(self, key: str) -> bool:
        """Check cache existence"""

        return self.get(key) is not None

    def clear(self) -> None:
        """Clear cache"""

        with self._lock:
            self._cache.clear()

    def stats(self) -> Dict[str, int]:
        """Cache statistics"""

        with self._lock:
            return {
                "entries": len(self._cache),
                "max_size": self.max_size,
            }

    def _evict_lru(self) -> None:
        """Evict least recently used entry"""

        if not self._cache:
            return

        lru_key = min(
            self._cache,
            key=lambda k: self._cache[k]["last_accessed"],
        )

        self._cache.pop(lru_key, None)