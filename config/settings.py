"""Pydantic Settings for RAG System Configuration"""
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment"""
    
    # Core
    environment: str = "development"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/rag_db"
    
    # Vector DB
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: Optional[str] = None
    
    # Graph DB
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # LLM
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    
    # Models
    default_embedding_model: str = "text-embedding-3-small"
    default_llm_model: str = "gpt-4-turbo"
    default_reranker_model: str = "ms-marco-MiniLM-L-12-v2"
    
    # Feature Flags
    use_semantic_cache: bool = True
    use_graphrag: bool = True
    use_multimodal_retrieval: bool = True
    use_live_web_search: bool = True
    enable_cost_optimization: bool = True
    
    # Limits
    rate_limit_queries_per_minute: int = 100
    rate_limit_tokens_per_day: int = 1000000
    max_context_tokens: int = 8000
    
    # Evaluation
    ragas_threshold: float = 0.7
    enable_offline_eval: bool = True
    enable_online_eval: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
