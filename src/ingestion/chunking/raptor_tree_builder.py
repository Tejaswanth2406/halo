"""RAPTOR tree builder (Sarthi et al. 2024)"""

from __future__ import annotations

import hashlib
from typing import List, Dict, Any


class RaptorTreeBuilder:
    """
    Build Recursive Abstractive Processing for
    Tree-Organized Retrieval (RAPTOR).

    Assumes an external summarizer is available.
    """

    def __init__(
        self,
        summarizer,
        branch_factor: int = 5,
        max_levels: int = 10,
    ):
        self.summarizer = summarizer
        self.branch_factor = branch_factor
        self.max_levels = max_levels

    def build_tree(
        self,
        chunks: list,
    ) -> dict:
        """Build RAPTOR tree from chunks"""

        if not chunks:
            return {}

        current_level = [
            {
                "id": self._id(chunk),
                "level": 0,
                "content": chunk,
                "children": [],
                "is_leaf": True,
            }
            for chunk in chunks
        ]

        tree_levels = [current_level]
        level = 0

        while (
            len(current_level) > 1
            and level < self.max_levels
        ):
            next_level = []

            for i in range(
                0,
                len(current_level),
                self.branch_factor,
            ):
                group = current_level[
                    i : i + self.branch_factor
                ]

                combined_text = "\n".join(
                    node["content"]
                    for node in group
                )

                summary = self.summarizer.summarize(
                    combined_text
                )

                parent = {
                    "id": self._id(
                        f"{level}:{summary}"
                    ),
                    "level": level + 1,
                    "content": summary,
                    "children": [
                        child["id"]
                        for child in group
                    ],
                    "is_leaf": False,
                }

                next_level.append(parent)

            tree_levels.append(next_level)
            current_level = next_level
            level += 1

        root = (
            current_level[0]
            if current_level
            else None
        )

        return {
            "root": root,
            "levels": tree_levels,
            "height": len(tree_levels),
            "total_nodes": sum(
                len(level_nodes)
                for level_nodes in tree_levels
            ),
            "branch_factor": self.branch_factor,
        }

    @staticmethod
    def _id(content: str) -> str:
        return hashlib.sha256(
            str(content).encode("utf-8")
        ).hexdigest()