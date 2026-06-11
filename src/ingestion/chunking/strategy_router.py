"""Chunking strategy router"""

from __future__ import annotations

from enum import Enum


class ChunkingStrategy(str, Enum):
    FIXED = "fixed"
    SEMANTIC = "semantic"
    HIERARCHICAL = "hierarchical"
    RAPTOR = "raptor"


class StrategyRouter:
    """Route documents to appropriate chunking strategy"""

    _MAPPING = {
        # Source code / structured
        "code": ChunkingStrategy.FIXED,
        "json": ChunkingStrategy.FIXED,
        "xml": ChunkingStrategy.FIXED,
        "csv": ChunkingStrategy.FIXED,
        "yaml": ChunkingStrategy.FIXED,
        "log": ChunkingStrategy.FIXED,

        # Prose
        "article": ChunkingStrategy.SEMANTIC,
        "blog": ChunkingStrategy.SEMANTIC,
        "email": ChunkingStrategy.SEMANTIC,
        "wiki": ChunkingStrategy.SEMANTIC,
        "manual": ChunkingStrategy.SEMANTIC,

        # Long documents
        "book": ChunkingStrategy.HIERARCHICAL,
        "research_paper": ChunkingStrategy.HIERARCHICAL,
        "report": ChunkingStrategy.HIERARCHICAL,
        "documentation": ChunkingStrategy.HIERARCHICAL,

        # Large enterprise knowledge bases
        "knowledge_base": ChunkingStrategy.RAPTOR,
        "corpus": ChunkingStrategy.RAPTOR,
        "enterprise_docs": ChunkingStrategy.RAPTOR,
    }

    def select_strategy(self, doc_type: str) -> str:
        """Select chunking strategy based on doc type"""

        if not doc_type:
            return ChunkingStrategy.SEMANTIC.value

        return self._MAPPING.get(
            doc_type.strip().lower(),
            ChunkingStrategy.SEMANTIC,
        ).value