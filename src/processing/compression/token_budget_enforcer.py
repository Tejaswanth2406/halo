"""Token budget enforcer"""

from __future__ import annotations

from typing import Optional


class TokenBudgetEnforcer:
    """Enforce hard token limit"""

    def __init__(self, tokenizer=None):
        """
        tokenizer: optional callable that returns token count
        If not provided, uses a rough heuristic (1 token ~ 4 chars)
        """
        self.tokenizer = tokenizer

    def enforce(self, text: str, max_tokens: int) -> str:
        """Enforce token budget"""

        if not text:
            return ""

        if max_tokens <= 0:
            return ""

        if self.tokenizer:
            return self._truncate_with_tokenizer(text, max_tokens)

        return self._truncate_heuristic(text, max_tokens)

    def _truncate_with_tokenizer(self, text: str, max_tokens: int) -> str:
        """Truncate using real tokenizer"""

        tokens = self.tokenizer.encode(text)

        if len(tokens) <= max_tokens:
            return text

        trimmed = tokens[:max_tokens]
        return self.tokenizer.decode(trimmed)

    def _truncate_heuristic(self, text: str, max_tokens: int) -> str:
        """Fallback character-based approximation"""

        approx_char_limit = max_tokens * 4

        if len(text) <= approx_char_limit:
            return text

        return text[:approx_char_limit].rstrip()