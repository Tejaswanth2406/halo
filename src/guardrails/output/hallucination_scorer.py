"""Hallucination scoring"""

import re
from typing import Set


class HallucinationScorer:
    """Score for hallucinations in response"""

    def score(self, response: str, context: str) -> float:
        """Calculate hallucination score (0.0 = grounded, 1.0 = highly hallucinated)"""

        if not response:
            return 0.0

        if not context:
            return 1.0

        response_tokens: Set[str] = {
            token
            for token in re.findall(r"\w+", response.lower())
            if len(token) > 3
        }

        context_tokens: Set[str] = {
            token
            for token in re.findall(r"\w+", context.lower())
            if len(token) > 3
        }

        if not response_tokens:
            return 0.0

        unsupported_tokens = response_tokens - context_tokens
        hallucination_score = len(unsupported_tokens) / len(response_tokens)

        return round(min(max(hallucination_score, 0.0), 1.0), 4)