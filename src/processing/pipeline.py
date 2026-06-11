"""Processing pipeline orchestration"""

from __future__ import annotations

from typing import List, Any, Optional


class ProcessingPipeline:
    """Orchestrate filtering, reranking, compression"""

    def __init__(
        self,
        filters: Optional[list] = None,
        rerankers: Optional[list] = None,
        compressor=None,
        deduplicator=None,
    ):
        self.filters = filters or []
        self.rerankers = rerankers or []
        self.compressor = compressor
        self.deduplicator = deduplicator

    async def process(self, documents: list) -> list:
        """Process retrieved documents"""

        if not documents:
            return []

        docs = documents

        # 1. Deduplication
        if self.deduplicator:
            docs = self.deduplicator.deduplicate(docs)

        # 2. Filtering stage (chain of filters)
        for f in self.filters:
            try:
                docs = f.filter(docs)
            except Exception:
                continue

        # 3. Reranking stage (cascade rerankers)
        for r in self.rerankers:
            try:
                docs = await r.rerank("", docs)
            except Exception:
                continue

        # 4. Compression stage
        if self.compressor:
            try:
                compressed = self.compressor.compress(docs)
                return [{"content": compressed, "compressed": True}]
            except Exception:
                pass

        return docs