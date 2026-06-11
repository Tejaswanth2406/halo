"""Conversation buffer with Redis"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

import redis.asyncio as redis


class ConversationBuffer:
    """Redis-backed conversation memory"""

    def __init__(
        self,
        redis_url: str,
        ttl_seconds: int = 86400,
        max_messages: int = 100,
        key_prefix: str = "conversation:",
    ):
        self.ttl_seconds = ttl_seconds
        self.max_messages = max_messages
        self.key_prefix = key_prefix

        self.redis = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )

    async def get_context(
        self,
        session_id: str,
    ) -> list:
        """Get conversation context"""

        if not session_id:
            raise ValueError(
                "session_id cannot be empty"
            )

        key = f"{self.key_prefix}{session_id}"

        messages = await self.redis.lrange(
            key,
            0,
            -1,
        )

        await self.redis.expire(
            key,
            self.ttl_seconds,
        )

        return [
            json.loads(message)
            for message in messages
        ]

    async def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append message to conversation"""

        if not session_id:
            raise ValueError(
                "session_id cannot be empty"
            )

        key = f"{self.key_prefix}{session_id}"

        message = {
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        pipe = self.redis.pipeline()

        pipe.rpush(
            key,
            json.dumps(
                message,
                ensure_ascii=False,
            ),
        )

        pipe.ltrim(
            key,
            -self.max_messages,
            -1,
        )

        pipe.expire(
            key,
            self.ttl_seconds,
        )

        await pipe.execute()

    async def clear_context(
        self,
        session_id: str,
    ) -> bool:
        """Delete conversation"""

        key = f"{self.key_prefix}{session_id}"

        return bool(
            await self.redis.delete(key)
        )

    async def context_size(
        self,
        session_id: str,
    ) -> int:
        """Number of stored messages"""

        key = f"{self.key_prefix}{session_id}"

        return int(
            await self.redis.llen(key)
        )

    async def close(self) -> None:
        """Close Redis connection"""

        await self.redis.close()