"""RankGPT listwise reranking"""

from __future__ import annotations

import json
from typing import List, Any, Dict, Optional


class RankGPTReranker:
    """Stage 4: Listwise LLM reranking"""

    def __init__(self, llm_client):
        self.llm_client = llm_client

    async def rerank(
        self,
        query: str,
        documents: list,
        k: int = 10,
    ) -> list:
        """Rerank using LLM listwise"""

        if not query or not documents:
            return []

        packed_docs = [
            {"id": i, "text": self._get_text(doc)}
            for i, doc in enumerate(documents)
        ]

        prompt = self._build_prompt(query, packed_docs)

        response = await self.llm_client.generate(prompt)

        ranked_ids = self._parse_response(response)

        id_to_doc = {i: doc for i, doc in enumerate(documents)}

        ranked_docs = [
            id_to_doc[i]
            for i in ranked_ids
            if i in id_to_doc
        ]

        # fallback if parsing fails
        if not ranked_docs:
            return documents[:k]

        return ranked_docs[:k]

    def _build_prompt(self, query: str, docs: list) -> str:
        return (
            "You are a precise listwise reranker.\n"
            "Given a query and candidate documents, rank them by relevance.\n\n"
            f"Query:\n{query}\n\n"
            "Documents:\n"
            + "\n".join(
                f"{d['id']}: {d['text']}" for d in docs
            )
            + "\n\n"
            "Return ONLY a JSON list of document IDs in descending order of relevance.\n"
            "Example: [2, 0, 5, 1]\n"
        )

    def _parse_response(self, response: str) -> List[int]:
        try:
            data = json.loads(response.strip())
            if isinstance(data, list):
                return [int(x) for x in data]
        except Exception:
            pass

        # fallback: extract digits
        import re

        return [
            int(x)
            for x in re.findall(r"\d+", response)
        ]

    def _get_text(self, doc: Any) -> str:
        if isinstance(doc, dict):
            return str(doc.get("content", ""))
        return str(doc)