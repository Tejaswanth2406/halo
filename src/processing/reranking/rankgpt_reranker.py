"""RankGPT listwise reranking"""

class RankGPTReranker:
    """Stage 4: Listwise LLM reranking"""
    
    async def rerank(self, query: str, documents: list, k: int = 10) -> list:
        """Rerank using LLM listwise"""
        pass
