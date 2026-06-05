"""Intent to retriever/model routing configuration"""
from typing import Dict, List, Any

ROUTING_TABLE: Dict[str, Dict[str, Any]] = {
    "factual_qa": {
        "retrievers": ["vector", "keyword", "graph"],
        "llm_model": "gpt-4-turbo",
        "enable_web_search": False,
        "enable_multimodal": False,
        "reranking_strategy": "cascade",
    },
    "creative_writing": {
        "retrievers": ["vector"],
        "llm_model": "gpt-4-turbo",
        "enable_web_search": False,
        "enable_multimodal": False,
        "reranking_strategy": "simple",
    },
    "code_generation": {
        "retrievers": ["vector", "keyword"],
        "llm_model": "gpt-4-turbo",
        "enable_web_search": False,
        "enable_multimodal": False,
        "reranking_strategy": "cascade",
    },
    "current_events": {
        "retrievers": ["web"],
        "llm_model": "gpt-4-turbo",
        "enable_web_search": True,
        "enable_multimodal": False,
        "reranking_strategy": "simple",
    },
    "multimodal_analysis": {
        "retrievers": ["vector", "multimodal"],
        "llm_model": "gpt-4-turbo",
        "enable_web_search": False,
        "enable_multimodal": True,
        "reranking_strategy": "cascade",
    },
    "comparison": {
        "retrievers": ["vector", "keyword", "graph"],
        "llm_model": "gpt-4-turbo",
        "enable_web_search": False,
        "enable_multimodal": False,
        "reranking_strategy": "listwise",
    }
}

def get_routing_config(intent: str) -> Dict[str, Any]:
    """Get routing config for intent, default to factual_qa"""
    return ROUTING_TABLE.get(intent, ROUTING_TABLE["factual_qa"])
