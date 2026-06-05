
"""Model registry with versioning"""
from enum import Enum
from typing import Dict, Any

class EmbeddingModels(str, Enum):
    """Available embedding models"""
    OPENAI_SMALL = "text-embedding-3-small"
    OPENAI_LARGE = "text-embedding-3-large"
    E5_SMALL = "intfloat/e5-small-v2"
    E5_BASE = "intfloat/e5-base-v2"
    BGEENCODER_SMALL = "BAAI/bge-small-en-v1.5"
    BGEENCODER_BASE = "BAAI/bge-base-en-v1.5"

class LLMModels(str, Enum):
    """Available LLM models"""
    GPT4_TURBO = "gpt-4-turbo"
    GPT4 = "gpt-4"
    GPT35_TURBO = "gpt-3.5-turbo"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"

class RerankerModels(str, Enum):
    """Available reranker models"""
    MS_MARCO_MINILM = "ms-marco-MiniLM-L-12-v2"
    COLBERT_V2 = "colbert-v2"
    BGE_RERANKER_BASE = "BAAI/bge-reranker-base"
    BGE_RERANKER_LARGE = "BAAI/bge-reranker-large"
    COHERE_RERANKER = "cohere-reranker"

MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "embeddings": {
        "default": EmbeddingModels.OPENAI_SMALL,
        "models": {
            EmbeddingModels.OPENAI_SMALL: {"dim": 1536, "provider": "openai"},
            EmbeddingModels.OPENAI_LARGE: {"dim": 3072, "provider": "openai"},
            EmbeddingModels.E5_SMALL: {"dim": 384, "provider": "huggingface"},
            EmbeddingModels.BGEENCODER_BASE: {"dim": 768, "provider": "huggingface"},
        }
    },
    "llms": {
        "default": LLMModels.GPT4_TURBO,
        "models": {
            LLMModels.GPT4_TURBO: {"context_window": 128000, "provider": "openai"},
            LLMModels.CLAUDE_3_OPUS: {"context_window": 200000, "provider": "anthropic"},
        }
    },
    "rerankers": {
        "default": RerankerModels.MS_MARCO_MINILM,
        "models": {
            RerankerModels.MS_MARCO_MINILM: {"latency_ms": 50, "provider": "huggingface"},
            RerankerModels.BGE_RERANKER_LARGE: {"latency_ms": 100, "provider": "huggingface"},
        }
    }
}
