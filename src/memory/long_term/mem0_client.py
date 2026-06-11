"""Mem0 integration for long-term memory"""

from __future__ import annotations

from typing import Optional, Dict, Any

from mem0 import Memory


class Mem0Client:
    """Mem0 API integration"""

    def __init__(
        self,
        api_key: str,
        user_id: str,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.user_id = user_id
        self.memory = Memory.from_config(
            config or {
                "llm": {
                    "provider": "openai",
                    "config": {
                        "api_key": api_key,
                    },
                }
            }
        )

    async def store_memory(
        self,
        content: str,
    ) -> None:
        """Store long-term memory"""

        if not content or not content.strip():
            raise ValueError(
                "content cannot be empty"
            )

        self.memory.add(
            content.strip(),
            user_id=self.user_id,
            metadata={
                "source": "rag_system",
                "memory_type": "long_term",
            },
        )

    async def search_memory(
        self,
        query: str,
        limit: int = 10,
    ) -> list:
        """Retrieve relevant memories"""

        return self.memory.search(
            query=query,
            user_id=self.user_id,
            limit=limit,
        )

    async def delete_memory(
        self,
        memory_id: str,
    ) -> None:
        """Delete memory"""

        self.memory.delete(memory_id)

    async def get_all_memories(self) -> list:
        """List all user memories"""

        return self.memory.get_all(
            user_id=self.user_id
        )