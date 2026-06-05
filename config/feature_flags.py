"""Feature flags for controlling system behavior"""
from dataclasses import dataclass

@dataclass
class FeatureFlags:
    """Toggle different RAG layers and features"""
    
    # Ingestion
    enable_pdf_parsing: bool = True
    enable_table_extraction: bool = True
    enable_image_ocr: bool = True
    enable_audio_transcription: bool = True
    
    # Retrieval
    enable_vector_retrieval: bool = True
    enable_keyword_retrieval: bool = True
    enable_graph_retrieval: bool = True
    enable_multimodal_retrieval: bool = True
    enable_web_search: bool = True
    
    # Processing
    enable_reranking: bool = True
    enable_compression: bool = True
    enable_deduplication: bool = True
    
    # Agent
    enable_multi_agent: bool = True
    enable_reflection: bool = True
    enable_cost_optimization: bool = True
    
    # Safety
    enable_guardrails: bool = True
    enable_pii_detection: bool = True
    enable_hallucination_detection: bool = True
    
    # Evaluation
    enable_ragas_eval: bool = True
    enable_ab_testing: bool = False

flags = FeatureFlags()
