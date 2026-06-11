"""
Synthesizer specialist agent
"""

from typing import List, Dict


class SynthesizerAgent:
    """
    Specialized writing and synthesis.
    """

    async def synthesize(
        self,
        context: List[Dict]
    ) -> str:
        """
        Generate a response from retrieved context.
        """

        if not context:
            return (
                "No relevant information found."
            )

        response_parts = []

        for document in context:
            content = (
                document.get(
                    "content",
                    ""
                ).strip()
            )

            if content:
                response_parts.append(
                    content
                )

        return "\n\n".join(
            response_parts
        )