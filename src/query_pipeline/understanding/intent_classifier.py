"""Intent classification"""

from __future__ import annotations

import re
from typing import List


class IntentClassifier:
    """Classify query intent"""

    def classify(self, query: str) -> str:
        """Classify intent: factual_qa, creative, code, etc"""

        if not query or not query.strip():
            return "unknown"

        q = query.lower().strip()

        code_signals = [
            "python", "java", "code", "function", "class",
            "implement", "debug", "error", "stack trace",
        ]

        creative_signals = [
            "story", "write", "poem", "generate", "compose",
            "fiction", "character", "novel",
        ]

        factual_signals = [
            "what is", "who is", "when", "where", "define",
            "explain", "meaning",
        ]

        comparison_signals = [
            "vs", "versus", "compare", "difference", "better",
        ]

        code_score = sum(1 for s in code_signals if s in q)
        creative_score = sum(1 for s in creative_signals if s in q)
        factual_score = sum(1 for s in factual_signals if s in q)
        comparison_score = sum(1 for s in comparison_signals if s in q)

        # prioritize strongest signal
        if code_score >= 1 or "```" in query:
            return "code"

        if comparison_score >= 1:
            return "comparison"

        if creative_score >= 1:
            return "creative"

        if factual_score >= 1:
            return "factual_qa"

        # fallback heuristic
        word_count = len(re.findall(r"\w+", q))

        if word_count > 20:
            return "multi_step_qa"

        return "general_qa"