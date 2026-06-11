"""
Critic specialist agent
"""

from difflib import SequenceMatcher


class CriticAgent:
    """
    Specialized verification agent.
    """

    MIN_CONFIDENCE = 0.60

    async def critique(
        self,
        response: str,
        context: str
    ) -> dict:
        """
        Verify response against context.
        """

        if not response:
            return {
                "approved": False,
                "confidence": 0.0,
                "issues": ["empty_response"]
            }

        if not context:
            return {
                "approved": False,
                "confidence": 0.0,
                "issues": ["missing_context"]
            }

        similarity = SequenceMatcher(
            None,
            response.lower(),
            context.lower()
        ).ratio()

        approved = (
            similarity >= self.MIN_CONFIDENCE
        )

        return {
            "approved": approved,
            "confidence": round(
                similarity,
                3
            ),
            "issues": []
            if approved
            else ["low_grounding_score"]
        }