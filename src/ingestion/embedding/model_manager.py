"""Embedding model manager for swapping models"""

class EmbeddingModelManager:
    """Manage embedding models with versioning"""
    
    def get_model(self, model_name: str):
        """Load embedding model"""
        pass
    
    def embed(self, text: str) -> list:
        """Embed text with current model"""
        pass
