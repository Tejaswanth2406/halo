"""Jailbreak pattern matching"""

import re


class JailbreakMatcher:
    """Detect known jailbreak patterns"""

    _PATTERNS = [
        r"\bdan\b",
        r"do anything now",
        r"developer mode",
        r"god mode",
        r"unrestricted mode",
        r"evil assistant",
        r"ignore safety",
        r"bypass restrictions",
        r"pretend to be",
        r"stay in character",
        r"roleplay as",
        r"jailbreak",
        r"ignore all previous instructions",
        r"override system prompt",
        r"simulate an ai with no rules",
        r"answer without limitations",
    ]

    def match(self, query: str) -> bool:
        """Check if query contains jailbreak attempt"""

        if not query:
            return False

        text = query.lower().strip()

        return any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in self._PATTERNS
        )