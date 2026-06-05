"""Agent message bus for LangGraph communication"""

class AgentMessageBus:
    """Inter-agent communication via message bus"""
    
    async def publish(self, sender: str, message: dict) -> None:
        """Publish message from agent"""
        pass
