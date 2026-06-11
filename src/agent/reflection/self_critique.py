"""
Self-critique reflection
"""

from typing import Dict


class SelfCritique:
    """Self-critique for reflection."""

    async def critique(
        self,
        response: str,
        context: str
    ) -> Dict:

        if not response:
            return {
                "approved": False,
                "issues": ["empty_response"]
            }

        issues = []

        response_lower = response.lower()
        context_lower = context.lower()

        # 1. Context usage check
        if len(context_lower) > 0:
            overlap = len(
                set(response_lower.split())
                & set(context_lower.split())
            )

            if overlap < 3:
                issues.append("low_context_grounding")

        # 2. Length sanity check
        if len(response.split()) < 5:
            issues.append("too_short")

        # 3. Overconfidence heuristic
        if "definitely" in response_lower and "not in context" in response_lower:
            issues.append("possible_hallucinated_certainty")

        return {
            "approved": len(issues) == 0,
            "issues": issues
        }