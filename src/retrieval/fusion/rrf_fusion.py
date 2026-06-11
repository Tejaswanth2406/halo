"""RRF (Reciprocal Rank Fusion)"""

from __future__ import annotations

from typing import Dict, List, Any, Tuple
from collections import defaultdict


class RRFFusion:
    """Fuse multiple retriever results using RRF"""

    def __init__(self, k: int = 60):
        self.k = k

    def fuse(self, retriever_results: dict) -> list:
        """Fuse results using RRF"""

        if not retriever_results:
            return []

        scores = defaultdict(float)
        doc_store = {}

        # retriever_results format:
        # {
        #   "bm25": [doc1, doc2],
        #   "vector": [doc2, doc3]
        # }

        for retriever_name, docs in retriever_results.items():
            if not docs:
                continue

            for rank, doc in enumerate(docs):
                doc_id = self._get_doc_id(doc)

                if not doc_id:
                    continue

                doc_store[doc_id] = doc

                # RRF score: 1 / (k + rank)
                scores[doc_id] += 1.0 / (self.k + rank + 1)

        ranked = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        return [doc_store[doc_id] for doc_id, _ in ranked]

    def _get_doc_id(self, doc: Any) -> str:
        if isinstance(doc, dict):
            return (
                str(doc.get("doc_id"))
                or str(doc.get("id"))
                or ""
            )
        return str(getattr(doc, "doc_id", "") or getattr(doc, "id", ""))
