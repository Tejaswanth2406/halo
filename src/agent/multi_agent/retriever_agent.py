"""
Retriever specialist agent
"""

from typing import List


class RetrieverAgent:
    """
    Specialized retrieval agent.
    """

    def __init__(self, retrieval_orchestrator):
        self.retrieval_orchestrator = (
            retrieval_orchestrator
        )

    async def retrieve(
        self,
        query: str
    ) -> List[dict]:
        """
        Retrieve relevant documents.
        """

        results = (
            await self.retrieval_orchestrator.retrieve(
                query=query
            )
        )

        return results