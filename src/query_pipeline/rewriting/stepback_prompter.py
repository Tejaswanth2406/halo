"""Step-back prompting for sub-question generation"""

from __future__ import annotations

from typing import List, Any


class StepBackPrompter:
    """Generate step-back sub-questions"""

    def __init__(self, llm_client):
        self.llm_client = llm_client

    def generate_substeps(self, query: str) -> list:
        """Generate step-back questions"""

        if not query or not query.strip():
            return []

        prompt = self._build_prompt(query)

        response = self.llm_client.generate(prompt)

        steps = self._parse(response)

        return steps or self._fallback(query)

    def _build_prompt(self, query: str) -> str:
        return (
            "You are a reasoning decomposition assistant.\n"
            "Convert the given query into step-back sub-questions.\n\n"
            "Rules:\n"
            "- Ask what must be true before answering\n"
            "- Identify missing assumptions\n"
            "- Break into prerequisite reasoning steps\n"
            "- Keep questions short and precise\n\n"
            f"Query:\n{query}\n\n"
            "Return ONLY a numbered list of sub-questions.\n"
        )

    def _parse(self, response: str) -> List[str]:
        if not response:
            return []

        steps: List[str] = []

        for line in response.split("\n"):
            line = line.strip()
            if not line:
                continue

            if line[0].isdigit():
                line = line.split(".", 1)[-1].strip()
            elif line.startswith("-"):
                line = line[1:].strip()

            if line:
                steps.append(line)

        return steps

    def _fallback(self, query: str) -> List[str]:
        return [
            f"What is the context required to answer: {query}?",
            f"What assumptions are needed for: {query}?",
            f"What are the key components involved in: {query}?",
        ]