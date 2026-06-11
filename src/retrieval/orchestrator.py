"""Retrieval orchestration with async fan-out"""

from __future__ import annotations

from typing import List, Any, Dict
import asyncio


class RetrieverOrchestrator:
    """Orchestrate multiple retrievers with circuit breaker"""

    def __init__(self, circuit_breaker=None):
        self.circuit_breaker = circuit_breaker

    async def retrieve(self, query: str, retrievers: list) -> list:
        """Fan out to multiple retrievers"""

        if not query or not retrievers:
            return []

        tasks = [
            self._safe_call(r, query)
            for r in retrievers
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        merged = []

        for res in results:
            if isinstance(res, Exception):
                continue
            if isinstance(res, list):
                merged.extend(res)

        return merged

    async def _safe_call(self, retriever, query: str):
        """
        Optionally wrap retriever call with circuit breaker.
        """

        async def _call():
            if hasattr(retriever, "retrieve"):
                result = retriever.retrieve(query)

                if hasattr(result, "__await__"):
                    return await result
                return result

            return []

        if self.circuit_breaker:
            return await self.circuit_breaker.call(_call)

        return await _call()