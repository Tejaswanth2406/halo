"""Embedding cache"""

from __future__ import annotations

import time
from threading import RLock
from typing import Dict, List, Optional, Any


class EmbeddingCache:
    """Cache embeddings by SHA256"""

    def __init__(
        self,
        max_size: int = 100_000,
        ttl_seconds: int = 86_400,
    ):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds

        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = RLock()

    def get(self, content_hash: str) -> Optional[List[float]]:
        """Get cached embedding"""

        if not content_hash:
            return None

        now = time.time()

        with self._lock:
            item = self._cache.get(content_hash)

            if item is None:
                return None

            if item["expires_at"] < now:
                self._cache.pop(content_hash, None)
                return None

            item["last_accessed"] = now

            return item["embedding"]

    def put(
        self,
        content_hash: str,
        embedding: List[float],
    ) -> None:
        """Store embedding"""

        if not content_hash:
            raise ValueError("content_hash is required")

        if not embedding:
            raise ValueError("embedding cannot be empty")

        now = time.time()

        with self._lock:
            if len(self._cache) >= self.max_size:
                lru_key = min(
                    self._cache,
                    key=lambda k: self._cache[k]["last_accessed"],
                )
                self._cache.pop(lru_key, None)

            self._cache[content_hash] = {
                "embedding": embedding,
                "created_at": now,
                "last_accessed": now,
                "expires_at": now + self.ttl_seconds,
            }

    def delete(self, content_hash: str) -> bool:
        """Delete cached embedding"""

        with self._lock:
            return self._cache.pop(content_hash, None) is not None

    def clear(self) -> None:
        """Clear cache"""

        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        """Current cache size"""

        with self._lock:
            return len(self._cache)
