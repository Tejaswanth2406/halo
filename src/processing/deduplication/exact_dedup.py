"""Exact deduplication using hash"""

from __future__ import annotations

import hashlib
from typing import List, Any, Set, Dict


class ExactDedup:
    """Remove exact duplicates using hash"""

    def __init__(self, normalize: bool = True):
        self.normalize = normalize

    def deduplicate(self, documents: list) -> list:
        """Remove exact duplicates"""

        if not documents:
            return []

        seen: Set[str] = set()
        result: List[Any] = []

        for doc in documents:
            content = self._normalize(doc)

            doc_hash = hashlib.sha256(
                content.encode("utf-8")
            ).hexdigest()

            if doc_hash in seen:
                continue

            seen.add(doc_hash)
            result.append(doc)

        return result

    def _normalize(self, doc: Any) -> str:
        """Normalize document before hashing"""

        if not self.normalize:
            return str(doc)

        if isinstance(doc, dict):
            # stable ordering for deterministic hashing
            return str(
                sorted(
                    (k, v)
                    for k, v in doc.items()
                )
            )

        return str(doc).strip()