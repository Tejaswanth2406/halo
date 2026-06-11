"""Entity extraction from queries"""

from __future__ import annotations

import re
from typing import List, Dict, Any, Optional


class EntityExtractor:
    """Extract entities from query"""

    def __init__(self):
        # simple heuristic patterns (can be swapped with spaCy / LLM later)
        self.patterns = [
            r"\b[A-Z][a-z]+\b",          # Capitalized words
            r"\b[A-Z]{2,}\b",            # Acronyms
            r"\"([^\"]+)\"",             # quoted entities
            r"'([^']+)'",
        ]

    def extract(self, query: str) -> list:
        """Extract entities from query"""

        if not query or not query.strip():
            return []

        entities = set()

        # regex-based extraction
        for pattern in self.patterns:
            matches = re.findall(pattern, query)
            for m in matches:
                if isinstance(m, tuple):
                    m = m[0]
                cleaned = m.strip()
                if cleaned:
                    entities.add(cleaned)

        # heuristic cleanup: remove very short tokens
        filtered = [
            e for e in entities
            if len(e) > 1 and not e.isdigit()
        ]

        return sorted(filtered)
