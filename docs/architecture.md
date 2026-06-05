# Architecture Guide

## System Design

RAG Production System is built on 10 distinct layers, each handling specific concerns:

### Layer 0: Ingestion (L0)
Runs offline on document upload
- **Parsers**: PDF, DOCX, HTML, images, audio
- **Enrichment**: Auto-tagging, entity linking, importance scoring
- **Chunking**: Fixed, semantic, hierarchical (RAPTOR)
- **Embedding**: Batched with caching
- **Indexing**: Vector (Qdrant), keyword (BM25), graph (Neo4j)
- **Quality**: Deduplication, quality scoring, PII scrubbing

### Layer 1: Guardrails (L1)
Safety and compliance
- **Input**: Injection detection, jailbreak matching, PII masking, toxicity
- **Auth**: JWT validation, tenant resolution, RBAC
- **Output**: Grounding verification, hallucination detection, PII check

### Layer 2: Query Pipeline (L2)
Query preprocessing
- **Understanding**: Intent classification, entity extraction, language detection
- **Rewriting**: HyDE, step-back prompting, multi-query generation
- **Routing**: Intent-based routing, query decomposition, dependency graphs

### Layer 3: Retrieval (L3)
7 retriever types with fusion
- **Vector**: Chroma, Qdrant, Pinecone
- **Keyword**: BM25, Elasticsearch
- **Graph**: Neo4j, GraphRAG communities
- **Multimodal**: ColPali, CLIP, table-to-SQL
- **Web**: Tavily live search
- **MCP**: GitHub, Gmail, Jira, Slack, etc.
- **Fusion**: RRF, weighted scoring

### Layer 4: Processing (L4)
Retrieved document refinement
- **Deduplication**: Exact, semantic, MMR diversity
- **Filtering**: Permission, freshness, quality
- **Reranking**: 4-stage cascade (BM25 → Cross-encoder → Cohere → LLM)
- **Compression**: LLMLingua, extractive, token budget

### Layer 5: Memory (L5)
Context management
- **Short-term**: Conversation buffer, turn summarizer
- **Long-term**: Mem0 integration, procedural memory
- **Working**: Agent scratchpad
- **Isolation**: Per-tenant memory namespacing

### Layer 6: Agent (L6)
Reasoning and orchestration
- **Reasoning**: ReAct framework with confidence scoring
- **Loop**: State machine (RETRIEVE → REASON → REFLECT → RESPOND)
- **Reflection**: Self-critique, gap detection, hallucination detection
- **Multi-agent**: Planner, retriever, critic, synthesizer agents
- **Response**: Generation, citation formatting, streaming

### Layer 7: Output Safety (L7)
Final verification
- **Grounding**: Verify claims in source chunks
- **Hallucination**: Score for hallucinations
- **PII**: Re-identification check
- **Human Loop**: Queue for human review if needed

### Layer 8: Cost Tracking (L8)
Financial controls
- **Tracking**: Token usage per call
- **Calculator**: Cost computation
- **Controller**: Per-user/tenant budgets
- **Optimizer**: Route to cheaper models under load

### Layer 9: Evaluation (L9)
Quality assurance
- **Offline**: RAGAS, synthetic generation
- **Online**: User feedback, engagement metrics
- **Diagnostics**: Layer-wise bottleneck detection
- **A/B Testing**: Experiment runner, significance testing

### Layer 10: Infrastructure (L10)
System reliability
- **Tracing**: Langfuse, OpenTelemetry
- **Caching**: L1 memory, L2 Redis, semantic
- **Resilience**: Circuit breaker, retry, degradation
- **Async**: Fully async with streaming
- **Alerts**: PagerDuty, Slack, quality regression

## Emerging Benchmarks (L9+)

13 new evaluation metrics beyond RAGAS:

1. **Context Relevance Precision** - Fraction of retrieved context that's relevant
2. **Contextual Faithfulness Score** - Response alignment with context AND external knowledge
3. **Multi-Hop Reasoning Accuracy** - Accuracy on multi-step reasoning chains
4. **RAG Diversity** - Coverage of diverse sources
5. **Query-Document Semantic Consistency** - Semantic alignment beyond lexical similarity
6. **Latency-Quality Tradeoff** - Quality at different latency budgets
7. **Adversarial Robustness Score** - Resistance to attacks
8. **Knowledge Cutoff Awareness** - Ability to know knowledge boundaries
9. **Cross-Lingual Retrieval Effectiveness** - Multilingual competence
10. **Source Attribution Accuracy** - Citation precision and completeness
11. **Retriever Disagreement Index** - Consensus between multiple retrievers
12. **Token Efficiency Ratio** - Useful tokens / total tokens spent
13. **Query-Document Temporal Alignment** - Freshness appropriateness

## Data Flow

```
User Query
    ↓
[L1] Input Guardrails → Injection check, PII mask
    ↓
[L2] Query Pipeline → Understand, rewrite, route
    ↓
[L3] Retrieval → Fan-out to 7 retriever types
    ↓
[L4] Processing → Deduplicate, filter, rerank, compress
    ↓
[L5] Memory → Short-term context + procedural memory
    ↓
[L6] Agent → ReAct reasoning, multi-agent orchestration
    ↓
[L7] Output Safety → Verify grounding, detect hallucinations
    ↓
[L8] Cost Track → Count tokens, check budgets
    ↓
[L9] Evaluation → RAGAS + 13 emerging benchmarks
    ↓
Final Response + Citations
    ↓
[L10] Infrastructure → Trace, cache, alert, monitor
```

## Configuration Hierarchy

1. **Global Settings** (config/settings.py)
2. **Tenant Config** (config/tenant_config.py)
3. **Intent Routing** (config/routing_table.py)
4. **Feature Flags** (config/feature_flags.py)
5. **Model Registry** (config/model_registry.py)

## Multi-Tenancy

- Redis namespaced per tenant
- Document-level RBAC
- Separate embedding indices
- Per-tenant cost budgets
- Isolated memory spaces

## Scaling Strategy

- **Horizontal**: Stateless async handlers
- **Retrieval**: Parallel fan-out with circuit breaker
- **Caching**: Multi-level (L1 → L2 → L3)
- **Models**: Version management + shadow mode testing
- **Monitoring**: Real-time dashboards + automated regression detection
