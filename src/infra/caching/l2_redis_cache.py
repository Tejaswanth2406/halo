"""Redis cache for exact queries"""

from __future__ import annotations

import json
from typing import Any, Optional

import redis.asyncio as redis


class L2RedisCache:
    """Redis cache by query hash"""

    def __init__(
        self,
        redis_url: str,
        ttl_seconds: int = 3600,
        key_prefix: str = "query_cache:",
    ):
        self.ttl_seconds = ttl_seconds
        self.key_prefix = key_prefix
        self.redis = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )

    async def get(self, query_hash: str) -> Any:
        """Get from Redis"""

        if not query_hash:
            return None

        key = f"{self.key_prefix}{query_hash}"

        try:
            value = await self.redis.get(key)

            if value is None:
                return None

            await self.redis.expire(
                key,
                self.ttl_seconds,
            )  # sliding TTL

            return json.loads(value)

        except Exception:
            return None

    async def put(
        self,
        query_hash: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """Store value in Redis"""

        if not query_hash:
            raise ValueError("query_hash is required")

        key = f"{self.key_prefix}{query_hash}"

        await self.redis.set(
            key,
            json.dumps(value, default=str),
            ex=ttl_seconds or self.ttl_seconds,
        )

    async def delete(self, query_hash: str) -> bool:
        """Delete cache entry"""

        key = f"{self.key_prefix}{query_hash}"

        return bool(await self.redis.delete(key))

    async def exists(self, query_hash: str) -> bool:
        """Check key existence"""

        key = f"{self.key_prefix}{query_hash}"

        return bool(await self.redis.exists(key))

    async def close(self) -> None:
        """Close Redis connection"""

        await self.redis.close()