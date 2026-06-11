"""Async query handler"""

from __future__ import annotations

import asyncio
from typing import Protocol, List


class QueryProcessor(Protocol):
    async def process(self, query: str) -> str: ...


class AsyncQueryHandler:
    """Asyncio throughout"""

    def __init__(
        self,
        processors: List[QueryProcessor],
        timeout_seconds: float = 30.0,
    ):
        self.processors = processors
        self.timeout_seconds = timeout_seconds

    async def handle_query(self, query: str) -> str:
        """Handle query asynchronously"""

        if not query or not query.strip():
            raise ValueError("query cannot be empty")

        if not self.processors:
            raise RuntimeError("no processors configured")

        async def _execute() -> str:
            current = query.strip()

            for processor in self.processors:
                current = await processor.process(current)

                if not current:
                    raise RuntimeError(
                        f"{processor.__class__.__name__} "
                        "returned an empty response"
                    )

            return current

        try:
            return await asyncio.wait_for(
                _execute(),
                timeout=self.timeout_seconds,
            )

        except asyncio.TimeoutError as exc:
            raise TimeoutError(
                f"query processing exceeded "
                f"{self.timeout_seconds}s timeout"
            ) from exc