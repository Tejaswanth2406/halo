"""Injection attack detection"""

import re


class InjectionDetector:
    """Detect prompt injection attacks"""

    _PATTERNS = [
        r"ignore\s+(all|previous|prior)\s+instructions",
        r"disregard\s+(all|previous|prior)\s+instructions",
        r"system\s+prompt",
        r"reveal\s+(your|the)\s+instructions",
        r"developer\s+message",
        r"bypass\s+safety",
        r"override\s+instructions",
        r"act\s+as\s+.*without\s+restrictions",
        r"jailbreak",
        r"do\s+anything\s+now",
        r"prompt\s+injection",
        r"forget\s+everything\s+above",
        r"ignore\s+your\s+rules",
    ]

    def detect(self, query: str) -> bool:
        """Check if query contains injection attack"""

        if not query:
            return False

        query = query.lower().strip()

        return any(
            re.search(pattern, query, re.IGNORECASE)
            for pattern in self._PATTERNS
        )