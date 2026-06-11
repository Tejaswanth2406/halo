"""Entity linking to knowledge graph"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LinkedEntity:
    text: str
    label: str
    start: int
    end: int
    kb_id: Optional[str] = None
    score: float = 0.0


class EntityLinker:
    """Link entities to knowledge graph"""

    # Simple built-in knowledge base (extend as needed)
    KNOWLEDGE_BASE: dict[str, dict] = {
        "python": {"id": "Q28865", "label": "LANGUAGE", "description": "Programming language"},
        "google": {"id": "Q95",    "label": "ORG",      "description": "Technology company"},
        "openai": {"id": "Q98764912", "label": "ORG",   "description": "AI research company"},
        "new york": {"id": "Q60",  "label": "GPE",      "description": "City in USA"},
        "london": {"id": "Q84",    "label": "GPE",      "description": "Capital of England"},
        "elon musk": {"id": "Q317521", "label": "PERSON", "description": "Entrepreneur"},
        "einstein": {"id": "Q937", "label": "PERSON",   "description": "Physicist"},
    }

    # Naive NER patterns (label -> regex)
    NER_PATTERNS: list[tuple[str, str]] = [
        ("DATE",    r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4})\b"),
        ("MONEY",   r"\$\s?\d+(?:,\d{3})*(?:\.\d{2})?|\b\d+(?:,\d{3})*(?:\.\d{2})?\s?(?:dollars?|euros?|pounds?)\b"),
        ("PERCENT", r"\b\d+(?:\.\d+)?\s?%"),
        ("EMAIL",   r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b"),
        ("URL",     r"https?://\S+"),
    ]

    def link_entities(self, text: str) -> list[LinkedEntity]:
        """Extract and link entities from text."""
        entities: list[LinkedEntity] = []
        used_spans: list[tuple[int, int]] = []

        # --- 1. KB-based matching (longest match first) ---
        lower_text = text.lower()
        kb_terms = sorted(self.KNOWLEDGE_BASE.keys(), key=len, reverse=True)

        for term in kb_terms:
            for match in re.finditer(re.escape(term), lower_text):
                start, end = match.start(), match.end()
                if self._overlaps(start, end, used_spans):
                    continue
                kb_entry = self.KNOWLEDGE_BASE[term]
                entities.append(LinkedEntity(
                    text=text[start:end],
                    label=kb_entry["label"],
                    start=start,
                    end=end,
                    kb_id=kb_entry["id"],
                    score=1.0,
                ))
                used_spans.append((start, end))

        # --- 2. Pattern-based NER ---
        for label, pattern in self.NER_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start, end = match.start(), match.end()
                if self._overlaps(start, end, used_spans):
                    continue
                entities.append(LinkedEntity(
                    text=match.group(),
                    label=label,
                    start=start,
                    end=end,
                    kb_id=None,
                    score=0.9,
                ))
                used_spans.append((start, end))

        # Sort by position in text
        entities.sort(key=lambda e: e.start)
        return entities

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _overlaps(start: int, end: int, used: list[tuple[int, int]]) -> bool:
        return any(s < end and start < e for s, e in used)