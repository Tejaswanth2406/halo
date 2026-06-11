"""Query decomposition for multi-hop queries"""

from __future__ import annotations

from typing import List, Any, Optional


class QueryDecomposer:
    """Decompose complex queries into sub-queries"""

    def __init__(self, llm_client):
        self.llm_client = llm_client

    def decompose(self, query: str) -> list:
        """Decompose query into sub-queries"""

        if not query or not query.strip():
            return []

        prompt = self._build_prompt(query)

        response = self.llm_client.generate(prompt)

        subqueries = self._parse(response)

        return subqueries or self._fallback(query)

    def _build_prompt(self, query: str) -> str:
        return (
            "You are a query decomposition engine for multi-hop retrieval.\n"
            "Break the query into atomic, answerable sub-queries.\n\n"
            "Rules:\n"
            "- Each sub-query should answer one fact or step\n"
            "- Preserve dependencies implicitly in order\n"
            "- Keep queries short and specific\n\n"
            f"Query:\n{query}\n\n"
            "Return ONLY a numbered list of sub-queries.\n"
        )

    def _parse(self, response: str) -> List[str]:
        if not response:
            return []

        subqueries: List[str] = []

        for line in response.split("\n"):
            line = line.strip()
            if not line:
                continue

            if line[0].isdigit():
                line = line.split(".", 1)[-1].strip()
            elif line.startswith("-"):
                line = line[1:].strip()

            if line:
                subqueries.append(line)

        return subqueries

    def _fallback(self, query: str) -> List[str]:
        return [
            f"What is required to answer: {query}?",
            f"What are the key entities in: {query}?",
            f"What is the final answer to: {query}?",
        ]