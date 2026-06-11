"""Toxicity classification"""

import re


class ToxicityClassifier:
    """Classify toxic content"""

    _TOXIC_PATTERNS = [
        r"\bhate\b",
        r"\bstupid\b",
        r"\bidiot\b",
        r"\bmoron\b",
        r"\bdumb\b",
        r"\bkill yourself\b",
        r"\bshut up\b",
        r"\bfool\b",
        r"\btrash\b",
        r"\bworthless\b",
        r"\bloser\b",
        r"\bpathetic\b",
        r"\bscum\b",
    ]

    def classify(self, text: str) -> float:
        """Classify toxicity score"""

        if not text:
            return 0.0

        text = text.lower()
        matches = sum(
            1
            for pattern in self._TOXIC_PATTERNS
            if re.search(pattern, text, re.IGNORECASE)
        )

        score = matches / len(self._TOXIC_PATTERNS)

        return round(min(score, 1.0), 4)