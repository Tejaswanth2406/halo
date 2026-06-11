"""Batch embedding with asyncio"""

from __future__ import annotations

import asyncio
from typing import List, Protocol, Any


class EmbeddingProvider(Protocol):
    async def embed(self, texts: List[str]) -> List[List[float]]:
        ...


class BatchEmbedder:
    """Generate embeddings in batches with async support"""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        batch_size: int = 128,
        max_concurrency: int = 8,
        timeout_seconds: float = 60.0,
    ):
        self.embedding_provider = embedding_provider
        self.batch_size = batch_size
        self.timeout_seconds = timeout_seconds
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def embed_batch(
        self,
        texts: list,
    ) -> list:
        """Embed batch of texts"""

        if not texts:
            return []

        batches = [
            texts[i : i + self.batch_size]
            for i in range(
                0,
                len(texts),
                self.batch_size,
            )
        ]

        async def process_batch(
            batch: List[str],
        ) -> List[List[float]]:
            async with self.semaphore:
                return await asyncio.wait_for(
                    self.embedding_provider.embed(batch),
                    timeout=self.timeout_seconds,
                )

        tasks = [
            asyncio.create_task(
                process_batch(batch)
            )
            for batch in batches
        ]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=False,
        )

        embeddings: List[Any] = []

        for batch_result in results:
            embeddings.extend(batch_result)

        if len(embeddings) != len(texts):
            raise RuntimeError(
                "Embedding count mismatch"
            )

        return embeddings