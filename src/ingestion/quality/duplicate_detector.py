"""
Duplicate detection
"""

import hashlib
import re
from typing import List


class DuplicateDetector:
    """Detect duplicate and near-duplicate documents."""

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text before hashing.
        """

        text = text.lower()

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        text = re.sub(
            r"[^\w\s]",
            "",
            text
        )

        return text.strip()

    def _hash_text(self, text: str) -> str:
        """
        Generate content hash.
        """

        normalized = self._normalize_text(text)

        return hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest()

    def find_duplicates(
        self,
        documents: List[dict]
    ) -> List[dict]:
        """
        Find duplicate documents.
        """

        seen_hashes = set()

        duplicates = []

        for document in documents:

            text = document.get(
                "text",
                ""
            )

            content_hash = self._hash_text(
                text
            )

            if content_hash in seen_hashes:
                duplicates.append(
                    document
                )
            else:
                seen_hashes.add(
                    content_hash
                )

        return duplicates