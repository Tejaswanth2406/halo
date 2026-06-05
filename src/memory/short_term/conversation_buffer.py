"""Conversation buffer with Redis"""

class ConversationBuffer:
    """Redis-backed conversation memory"""
    
    async def get_context(self, session_id: str) -> list:
        """Get conversation context"""
        pass
