"""Streaming bus for token stream"""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator, Protocol, Optional


class StreamingLLM(Protocol):
    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        ...


class StreamingBus:
    """Stream tokens from LLM"""

    def __init__(
        self,
        llm: StreamingLLM,
        timeout_seconds: float = 60.0,
        max_token_size: int = 8192,
    ):
        self.llm = llm
        self.timeout_seconds = timeout_seconds
        self.max_token_size = max_token_size

    async def stream_tokens(
        self,
        query: str,
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens"""

        if not query or not query.strip():
            raise ValueError("query cannot be empty")

        queue: asyncio.Queue[Optional[str]] = asyncio.Queue()

        async def producer() -> None:
            try:
                async for token in self.llm.stream(query):
                    if token is None:
                        continue

                    token = str(token)

                    if len(token) > self.max_token_size:
                        token = token[: self.max_token_size]

                    await queue.put(token)

            finally:
                await queue.put(None)

        producer_task = asyncio.create_task(producer())

        try:
            while True:
                token = await asyncio.wait_for(
                    queue.get(),
                    timeout=self.timeout_seconds,
                )

                if token is None:
                    break

                yield token

        finally:
            if not producer_task.done():
                producer_task.cancel()

                try:
                    await producer_task
                except asyncio.CancelledError:
                    pass