"""Multi-query generator"""

from __future__ import annotations

from typing import List, Any, Optional


class MultiQueryGenerator:
    """Generate query variants for retrieval"""

    def __init__(self, llm_client):
        self.llm_client = llm_client

    def generate_variants(
        self,
        query: str,
        num_variants: int = 3,
    ) -> list:
        """Generate parallel query variants"""

        if not query or not query.strip():
            return []

        prompt = self._build_prompt(query, num_variants)

        response = self.llm_client.generate(prompt)

        variants = self._parse(response)

        if not variants:
            return self._fallback(query, num_variants)

        return variants[:num_variants]

    def _build_prompt(self, query: str, n: int) -> str:
        return (
            "You are a query rewriting system for retrieval.\n"
            "Generate semantically equivalent but diverse search queries.\n\n"
            f"Original query:\n{query}\n\n"
            f"Generate {n} alternative queries that preserve intent.\n"
            "Return as a numbered list only.\n"
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
            if line[0].isdigit():
                line = line.split(".", 1)[-1].strip()
            elif line.startswith("-"):
                line = line[1:].strip()

            if line:
                cleaned.append(line)

        return cleaned

    def _fallback(self, query: str, n: int) -> List[str]:
        return [query for _ in range(n)]