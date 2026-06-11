"""
Agent message bus for LangGraph communication
"""

import asyncio
from collections import defaultdict


class AgentMessageBus:
    """
    Inter-agent communication bus.
    """

    def __init__(self):
        self.channels = defaultdict(asyncio.Queue)

    async def publish(
        self,
        sender: str,
        message: dict
    ) -> None:
        """
        Publish a message.

        Example:
        {
            "recipient": "retriever",
            "task": "retrieve_docs",
            "query": "vacation policy"
        }
        """

        recipient = message.get(
            "recipient"
        )

        if not recipient:
            raise ValueError(
                "recipient required"
            )

        envelope = {
            "sender": sender,
            "message": message
        }

        await self.channels[
            recipient
        ].put(envelope)

    async def subscribe(
        self,
        agent_name: str
    ) -> dict:
        """
        Wait for next message.
        """

        return await self.channels[
            agent_name
        ].get()