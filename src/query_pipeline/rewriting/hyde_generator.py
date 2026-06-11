"""HyDE (Hypothetical Document Embeddings) generator"""

from __future__ import annotations

from typing import List, Any, Optional


class HyDEGenerator:
    """Generate hypothetical documents for query"""

    def __init__(self, llm_client, num_hypotheses: int = 3):
        self.llm_client = llm_client
        self.num_hypotheses = num_hypotheses

    def generate(self, query: str) -> list:
        """Generate hypothetical documents"""

        if not query or not query.strip():
            return []

        prompt = self._build_prompt(query)

        response = self.llm_client.generate(prompt)

        hypotheses = self._parse(response)

        if not hypotheses:
            return self._fallback(query)

        return hypotheses[: self.num_hypotheses]

    def _build_prompt(self, query: str) -> str:
        return (
            "You are a helpful assistant generating hypothetical documents.\n"
            "Given a query, write realistic passages that could answer it.\n\n"
            f"Query:\n{query}\n\n"
            f"Generate {self.num_hypotheses} different detailed passages.\n"
            "Return them as a numbered list.\n"
        )

    def _parse(self, response: str) -> List[str]:
        if not response:
            return []

        lines = [
            line.strip()
            for line in response.split("\n")
            if line.strip()
        ]

        cleaned = []

        for line in lines:
            # remove numbering like "1." or "- "
            if line[0].isdigit():
                line = line.split(".", 1)[-1].strip()
            elif line.startswith("-"):
                line = line[1:].strip()

            if line:
                cleaned.append(line)

        return cleaned

    def _fallback(self, query: str) -> List[str]:
        return [
            f"A document explaining {query} in detail.",
            f"An article describing key aspects of {query}.",
            f"A technical overview of {query} with examples.",
        ]