"""
Response generation
"""

from typing import List, Dict


class ResponseGenerator:
    """Generate final response."""

    async def generate(
        self,
        context: List[Dict]
    ) -> str:
        """
        Generate response from context.
        """

        if not context:
            return "No relevant information found."

        parts = []

        for doc in context:
            text = doc.get("content", "").strip()

            if text:
                parts.append(text)

        return "\n\n".join(parts)
