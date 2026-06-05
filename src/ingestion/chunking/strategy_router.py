"""Chunking strategy router"""

class StrategyRouter:
    """Route documents to appropriate chunking strategy"""
    
    def select_strategy(self, doc_type: str) -> str:
        """Select chunking strategy based on doc type"""
        pass
