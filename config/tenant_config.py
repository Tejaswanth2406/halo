"""Per-tenant configuration overrides"""
from typing import Dict, Any, Optional

class TenantConfig:
    """Per-tenant customization"""
    
    def __init__(self):
        self.tenant_configs: Dict[str, Dict[str, Any]] = {
            "default": {
                "max_documents": 100000,
                "max_queries_per_day": 10000,
                "max_tokens_per_day": 1000000,
                "enabled_retrievers": ["vector", "keyword", "graph"],
                "embedding_model": "text-embedding-3-small",
                "llm_model": "gpt-4-turbo",
                "reranker_model": "ms-marco-MiniLM-L-12-v2",
                "enable_web_search": False,
                "enable_multimodal": False,
                "pii_redaction": True,
                "hallucination_detection": True,
            }
        }
    
    def get_config(self, tenant_id: str) -> Dict[str, Any]:
        """Get configuration for specific tenant"""
        return self.tenant_configs.get(tenant_id, self.tenant_configs["default"])
    
    def set_config(self, tenant_id: str, config: Dict[str, Any]):
        """Override configuration for specific tenant"""
        self.tenant_configs[tenant_id] = config
    
    def update_config(self, tenant_id: str, updates: Dict[str, Any]):
        """Update specific tenant configuration"""
        if tenant_id not in self.tenant_configs:
            self.tenant_configs[tenant_id] = self.tenant_configs["default"].copy()
        self.tenant_configs[tenant_id].update(updates)

tenant_config = TenantConfig()
