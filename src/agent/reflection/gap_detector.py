"""
Gap detector for missing information
"""

from typing import List
import re


class GapDetector:
    """Detect missing information gaps in response vs context/query."""

    async def detect_gaps(
        self,
        response: str,
        context: str
    ) -> List[str]:
        """
        Returns list of detected gaps.
        """

        gaps = []

        if not response:
            return ["empty_response"]

        response_lower = response.lower()
        context_lower = context.lower()

        # 1. Check if context info is used at all
        context_sentences = [
            s.strip()
            for s in context_lower.split(".")
            if s.strip()
        ]

        missing_context_items = 0

        for sentence in context_sentences:
            if sentence not in response_lower:
                missing_context_items += 1

        if missing_context_items > len(context_sentences) * 0.5:
            gaps.append("low_context_coverage")

        # 2. Detect numeric/data missing
        numbers_in_context = re.findall(r"\d+", context_lower)
        numbers_in_response = re.findall(r"\d+", response_lower)

        if numbers_in_context and not numbers_in_response:
            gaps.append("missing_numeric_information")

        # 3. Detect length mismatch (very rough heuristic)
        if len(response.split()) < len(context.split()) * 0.2:
            gaps.append("under_informative_response")

        return gaps