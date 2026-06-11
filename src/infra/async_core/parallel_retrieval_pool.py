"""Parallel retrieval pool"""

from __future__ import annotations

import asyncio
from typing import Any, List


class ParallelRetrievalPool:
    """Async retriever pool"""

    def __init__(
        self,
        timeout_seconds: float = 10.0,
        max_concurrency: int = 20,
    ):
        self.timeout_seconds = timeout_seconds
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def retrieve_parallel(
        self,
        query: str,
        retrievers: list,
    ) -> list:
        """Retrieve from multiple retrievers in parallel"""

        if not query:
            raise ValueError("query cannot be empty")

        if not retrievers:
            return []

        async def _retrieve(retriever: Any):
            async with self.semaphore:
                try:
                    result = await asyncio.wait_for(
                        retriever.retrieve(query),
                        timeout=self.timeout_seconds,
                    )

                    return {
                        "retriever": retriever.__class__.__name__,
                        "success": True,
                        "documents": result or [],
                    }

                except Exception as exc:
                    return {
                        "retriever": retriever.__class__.__name__,
                        "success": False,
                        "error": str(exc),
                        "documents": [],
                    }

        tasks = [
            asyncio.create_task(_retrieve(retriever))
            for retriever in retrievers
        ]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=False,
        )

        merged_documents: List[Any] = []
        seen = set()

        for result in results:
            for doc in result["documents"]:
                doc_id = getattr(doc, "id", str(doc))

                if doc_id not in seen:
                    seen.add(doc_id)
                    merged_documents.append(doc)

        return merged_documents