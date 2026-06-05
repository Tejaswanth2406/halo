"""Cohere reranker"""

class CohereReranker:
    """Stage 3: Cohere reranker API"""
    
    async def rerank(self, query: str, documents: list, k: int = 10) -> list:
        """Rerank using Cohere API"""
        pass
