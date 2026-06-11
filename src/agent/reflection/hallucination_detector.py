"""
Hallucination detector
"""

from typing import List
import difflib


class HallucinationDetector:
    """Detect claims not grounded in context."""

    async def detect(
        self,
        response: str,
        context: str
    ) -> List[str]:
        """
        Returns list of hallucinated claims.
        """

        hallucinations = []

        if not response or not context:
            return ["empty_input"]

        response_sentences = [
            s.strip()
            for s in response.split(".")
            if s.strip()
        ]

        context_lower = context.lower()

        for sentence in response_sentences:

            sentence_lower = sentence.lower()

            # crude grounding check
            similarity = difflib.SequenceMatcher(
                None,
                sentence_lower,
                context_lower
            ).ratio()

            # threshold heuristic
            if similarity < 0.4:
                hallucinations.append(sentence)

        return hallucinations