"""Graceful degradation"""

from __future__ import annotations

from typing import List, Any


class GracefulDegradation:
    """Fall back to fewer retrievers"""

    def __init__(
        self,
        min_retrievers: int = 1,
        max_failure_rate: float = 0.5,
    ):
        self.min_retrievers = min_retrievers
        self.max_failure_rate = max_failure_rate

    async def degrade(
        self,
        retrievers: list,
    ) -> list:
        """Get degraded retriever list"""

        if not retrievers:
            return []

        healthy = []
        unhealthy = []

        for retriever in retrievers:
            health_score = getattr(
                retriever,
                "health_score",
                1.0,
            )

            error_rate = getattr(
                retriever,
                "error_rate",
                0.0,
            )

            latency_ms = getattr(
                retriever,
                "latency_ms",
                0,
            )

            score = (
                (health_score * 0.6)
                + ((1.0 - error_rate) * 0.3)
                + (max(0, 1 - latency_ms / 5000) * 0.1)
            )

            if error_rate <= self.max_failure_rate:
                healthy.append((score, retriever))
            else:
                unhealthy.append((score, retriever))

        healthy.sort(key=lambda x: x[0], reverse=True)
        unhealthy.sort(key=lambda x: x[0], reverse=True)

        selected = [
            retriever
            for _, retriever in healthy
        ]

        if len(selected) < self.min_retrievers:
            deficit = self.min_retrievers - len(selected)

            selected.extend(
                retriever
                for _, retriever in unhealthy[:deficit]
            )

        return selected[: max(self.min_retrievers, len(selected))]
