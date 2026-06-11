"""Semantic chunking for prose"""

from __future__ import annotations

import re
import hashlib
from typing import List, Dict, Any


class SemanticChunker:
    """Chunk based on semantic boundaries"""

    def __init__(
        self,
        min_chunk_size: int = 200,
        max_chunk_size: int = 1200,
    ):
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

    def chunk(self, text: str) -> list:
        """Split text into semantic chunks"""

        if not text or not text.strip():
            return []

        paragraphs = [
            p.strip()
            for p in re.split(r"\n\s*\n", text)
            if p.strip()
        ]

        chunks: List[Dict[str, Any]] = []

        buffer = []
        current_size = 0
        chunk_index = 0

        for paragraph in paragraphs:
            paragraph_size = len(paragraph)

            if (
                current_size + paragraph_size > self.max_chunk_size
                and buffer
            ):
                content = "\n\n".join(buffer)

                chunks.append(
                    {
                        "chunk_id": self._chunk_id(content),
                        "chunk_index": chunk_index,
                        "size": len(content),
                        "content": content,
                    }
                )

                chunk_index += 1
                buffer = []
                current_size = 0

            buffer.append(paragraph)
            current_size += paragraph_size

            if current_size >= self.min_chunk_size:
                content = "\n\n".join(buffer)

                chunks.append(
                    {
                        "chunk_id": self._chunk_id(content),
                        "chunk_index": chunk_index,
                        "size": len(content),
                        "content": content,
                    }
                )

                chunk_index += 1
                buffer = []
                current_size = 0

        if buffer:
            content = "\n\n".join(buffer)

            chunks.append(
                {
                    "chunk_id": self._chunk_id(content),
                    "chunk_index": chunk_index,
                    "size": len(content),
                    "content": content,
                }
            )

        return chunks

    @staticmethod
    def _chunk_id(content: str) -> str:
        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()