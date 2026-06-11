"""Fixed-size chunking for code and structured data"""

from __future__ import annotations

from typing import List, Dict, Any
import hashlib


class FixedChunker:
    """Chunk documents into fixed-size chunks"""

    def chunk(
        self,
        text: str,
        chunk_size: int = 512,
        overlap: int = 50,
    ) -> List[Dict[str, Any]]:
        """Split text into fixed-size chunks"""

        if not text:
            return []

        if chunk_size <= 0:
            raise ValueError("chunk_size must be > 0")

        if overlap < 0:
            raise ValueError("overlap must be >= 0")

        if overlap >= chunk_size:
            raise ValueError(
                "overlap must be smaller than chunk_size"
            )

        chunks: List[Dict[str, Any]] = []

        start = 0
        chunk_index = 0
        step = chunk_size - overlap
        text_length = len(text)

        while start < text_length:
            end = min(start + chunk_size, text_length)

            content = text[start:end]

            chunks.append(
                {
                    "chunk_id": hashlib.sha256(
                        f"{chunk_index}:{content}".encode()
                    ).hexdigest(),
                    "chunk_index": chunk_index,
                    "start_offset": start,
                    "end_offset": end,
                    "length": len(content),
                    "content": content,
                }
            )

            chunk_index += 1
            start += step

        return chunks