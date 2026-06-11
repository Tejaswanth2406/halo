"""Hierarchical chunking using RAPTOR-inspired structure"""

from __future__ import annotations

import hashlib
from typing import Dict, List, Any


class HierarchicalChunker:
    """
    Create hierarchical chunk structure for long documents.

    Levels:
    - Root document
    - Sections
    - Paragraph groups
    - Leaf chunks
    """

    def __init__(
        self,
        section_chunk_size: int = 4000,
        paragraph_chunk_size: int = 1000,
        leaf_chunk_size: int = 300,
    ):
        self.section_chunk_size = section_chunk_size
        self.paragraph_chunk_size = paragraph_chunk_size
        self.leaf_chunk_size = leaf_chunk_size

    def chunk(self, text: str) -> dict:
        """Create hierarchical chunks"""

        if not text or not text.strip():
            return {}

        text = text.strip()

        root = {
            "id": self._id(text),
            "type": "document",
            "length": len(text),
            "summary": self._summary(text),
            "children": [],
        }

        sections = self._split_text(
            text,
            self.section_chunk_size,
        )

        for section_idx, section in enumerate(sections):
            section_node = {
                "id": self._id(
                    f"section:{section_idx}:{section}"
                ),
                "parent": root["id"],
                "type": "section",
                "index": section_idx,
                "summary": self._summary(section),
                "length": len(section),
                "children": [],
            }

            paragraph_groups = self._split_text(
                section,
                self.paragraph_chunk_size,
            )

            for para_idx, paragraph_group in enumerate(
                paragraph_groups
            ):
                para_node = {
                    "id": self._id(
                        f"para:{section_idx}:{para_idx}"
                    ),
                    "parent": section_node["id"],
                    "type": "paragraph_group",
                    "index": para_idx,
                    "summary": self._summary(
                        paragraph_group
                    ),
                    "length": len(paragraph_group),
                    "children": [],
                }

                leaf_chunks = self._split_text(
                    paragraph_group,
                    self.leaf_chunk_size,
                )

                for leaf_idx, leaf in enumerate(
                    leaf_chunks
                ):
                    para_node["children"].append(
                        {
                            "id": self._id(
                                f"leaf:{section_idx}:{para_idx}:{leaf_idx}"
                            ),
                            "parent": para_node["id"],
                            "type": "leaf",
                            "index": leaf_idx,
                            "length": len(leaf),
                            "content": leaf,
                        }
                    )

                section_node["children"].append(
                    para_node
                )

            root["children"].append(section_node)

        return root

    def _split_text(
        self,
        text: str,
        max_size: int,
    ) -> List[str]:
        chunks = []

        start = 0

        while start < len(text):
            end = min(
                start + max_size,
                len(text),
            )

            if end < len(text):
                split_point = text.rfind(
                    " ",
                    start,
                    end,
                )

                if split_point > start:
                    end = split_point

            chunks.append(
                text[start:end].strip()
            )

            start = end

        return [c for c in chunks if c]

    def _summary(
        self,
        text: str,
        max_words: int = 30,
    ) -> str:
        words = text.split()

        if len(words) <= max_words:
            return text

        return " ".join(
            words[:max_words]
        ) + "..."

    def _id(self, text: str) -> str:
        return hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()