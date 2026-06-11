"""Embedding cache to avoid recomputation"""

from __future__ import annotations

import time
from threading import RLock
from collections import OrderedDict
from typing import Dict, List, Optional


class EmbeddingCache:
    """Cache embeddings by content hash"""

    def __init__(
        self,
        max_entries: int = 100_000,
        ttl_seconds: int = 86_400,
    ):
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds

        self._cache: OrderedDict[str, Dict] = OrderedDict()
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

            if item["expires_at"] <= now:
                self._cache.pop(content_hash, None)
                return None

            self._cache.move_to_end(content_hash)

            return item["embedding"]

    def set(
        self,
        content_hash: str,
        embedding: list,
    ) -> None:
        """Cache embedding"""

        if not content_hash:
            raise ValueError(
                "content_hash cannot be empty"
            )

        if not embedding:
            raise ValueError(
                "embedding cannot be empty"
            )

        now = time.time()

        with self._lock:
            self._cache[content_hash] = {
                "embedding": embedding,
                "created_at": now,
                "expires_at": now + self.ttl_seconds,
            }

            self._cache.move_to_end(content_hash)

            while len(self._cache) > self.max_entries:
                self._cache.popitem(last=False)

    def delete(self, content_hash: str) -> bool:
        """Remove cached embedding"""

        with self._lock:
            return (
                self._cache.pop(content_hash, None)
                is not None
            )

    def clear(self) -> None:
        """Clear cache"""

        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        """Current cache size"""

        with self._lock:
            return len(self._cache)