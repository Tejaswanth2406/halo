"""
Confidence scoring
"""

from difflib import SequenceMatcher


class ConfidenceScorer:
    """Score confidence in response."""

    def score(
        self,
        response: str,
        context: str
    ) -> float:
        """
        Returns confidence score between 0 and 1.
        """

        if not response or not context:
            return 0.0

        response = response.lower()
        context = context.lower()

        similarity = SequenceMatcher(
            None,
            response,
            context
        ).ratio()

        return round(similarity, 3)