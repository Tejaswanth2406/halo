"""Memory manager orchestration"""

from __future__ import annotations

from typing import Dict, Any, Optional, List


class MemoryManager:
    """Coordinate all memory types"""

    def __init__(
        self,
        procedural_memory=None,
        conversation_buffer=None,
        scratchpad=None,
        semantic_cache=None,
        tenant_isolator=None,
    ):
        self.procedural_memory = procedural_memory
        self.conversation_buffer = conversation_buffer
        self.scratchpad = scratchpad
        self.semantic_cache = semantic_cache
        self.tenant_isolator = tenant_isolator

    async def retrieve_memory(
        self,
        context_type: str,
        session_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        query: Optional[str] = None,
    ) -> dict:
        """Retrieve relevant memory"""

        if not context_type:
            raise ValueError("context_type is required")

        memory_bundle: Dict[str, Any] = {
            "context_type": context_type,
            "conversation": None,
            "procedural": None,
            "scratchpad": None,
            "semantic_cache": None,
            "tenant": None,
        }

        if tenant_id and self.tenant_isolator:
            memory_bundle["tenant"] = await self.tenant_isolator.get_tenant_memory(
                tenant_id
            )

        if session_id and self.conversation_buffer:
            memory_bundle["conversation"] = await self.conversation_buffer.get_context(
                session_id
            )

        if self.procedural_memory and session_id:
            memory_bundle["procedural"] = await self.procedural_memory.get_preferences(
                session_id
            )

        if self.scratchpad:
            memory_bundle["scratchpad"] = await self.scratchpad.get_thoughts()

        if query and self.semantic_cache:
            memory_bundle["semantic_cache"] = await self.semantic_cache.get_similar(
                query
            )

        return memory_bundle