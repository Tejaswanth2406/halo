"""Weighted score fusion"""

from __future__ import annotations

from typing import Dict, List, Any
from collections import defaultdict


class WeightedFusion:
    """Fuse results using weighted scoring"""

    def fuse(self, retriever_results: dict, weights: dict) -> list:
        """Fuse results with weights"""

        if not retriever_results:
            return []

        scores = defaultdict(float)
        doc_store = {}

        # Expected format:
        # retriever_results = {
        #   "bm25": [(doc, score), ...],
        #   "vector": [(doc, score), ...]
        # }

        for retriever, items in retriever_results.items():
            if not items:
                continue

            weight = float(weights.get(retriever, 1.0))

            for rank, item in enumerate(items):
                # support (doc, score) or doc-only
                if isinstance(item, tuple) and len(item) == 2:
                    doc, score = item
                else:
                    doc, score = item, 1.0

                doc_id = self._get_doc_id(doc)
                if not doc_id:
                    continue

                doc_store[doc_id] = doc

                # weighted contribution
                scores[doc_id] += weight * float(score)

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