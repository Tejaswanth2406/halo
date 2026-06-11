"""LLMLingua compression"""

from __future__ import annotations

from typing import List, Any, Optional


class LLMLinguaCompressor:
    """Compress context using LLMLingua"""

    def __init__(self, llmlingua_client):
        self.llmlingua = llmlingua_client

    def compress(
        self,
        documents: list,
        max_tokens: int = 2000,
    ) -> str:
        """Compress documents"""

        if not documents:
            return ""

        text = self._merge_documents(documents)

        if not text.strip():
            return ""

        result = self.llmlingua.compress(
            text=text,
            target_token=max_tokens,
        )

        if isinstance(result, dict):
            compressed = result.get("compressed_text")
        else:
            compressed = result

        if not compressed:
            raise RuntimeError(
                "LLMLingua returned empty output"
            )

        return str(compressed).strip()

    def _merge_documents(self, documents: list) -> str:
        """Merge docs into single context block"""

        merged = []

        for doc in documents:
            if isinstance(doc, dict):
                merged.append(doc.get("content", ""))
            else:
                merged.append(str(doc))

        return "\n\n".join(
            part.strip()
            for part in merged
            if part and str(part).strip()
        )