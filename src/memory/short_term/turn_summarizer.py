"""Turn summarizer"""

from __future__ import annotations

from typing import List, Dict, Any, Optional


class TurnSummarizer:
    """Compress old conversation turns"""

    def __init__(self, llm_client):
        self.llm_client = llm_client

    async def summarize_turns(self, turns: list) -> str:
        """Summarize conversation turns"""

        if not turns:
            return ""

        formatted = self._format_turns(turns)

        prompt = (
            "You are a highly precise conversation compressor.\n"
            "Summarize the following dialogue turns while preserving:\n"
            "- Key user intent\n"
            "- Important facts and decisions\n"
            "- Entities and constraints\n\n"
            "Do NOT add new information.\n\n"
            f"Conversation:\n{formatted}\n\n"
            "Summary:"
        )

        response = await self.llm_client.generate(prompt)

        if not response:
            raise RuntimeError("LLM returned empty summary")

        return response.strip()

    def _format_turns(self, turns: list) -> str:
        """Format turns for summarization"""

        lines = []

        for i, turn in enumerate(turns):
            if isinstance(turn, dict):
                role = turn.get("role", "unknown")
                content = turn.get("content", "")
            else:
                role = "unknown"
                content = str(turn)

            lines.append(f"{i + 1}. {role}: {content}")

        return "\n".join(lines)