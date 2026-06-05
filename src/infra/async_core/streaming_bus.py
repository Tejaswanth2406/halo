"""Streaming bus for token stream"""

class StreamingBus:
    """Stream tokens from LLM"""
    
    async def stream_tokens(self, query: str) -> AsyncGenerator:
        """Stream response tokens"""
        pass
