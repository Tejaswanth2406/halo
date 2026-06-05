# Configuration Guide

## Environment Setup

Create `.env` file from template:
```bash
cp .env.example .env
```

### API Keys Required
- `OPENAI_API_KEY` - GPT-4/embedding models
- `ANTHROPIC_API_KEY` - Claude models (optional)
- `COHERE_API_KEY` - Reranker API (optional)
- `TAVILY_API_KEY` - Web search (optional)

### Database Configuration

#### Vector Database
```env
# Qdrant (production)
QDRANT_HOST=qdrant.example.com
QDRANT_PORT=6333
QDRANT_API_KEY=xxx

# Or Pinecone (managed)
PINECONE_API_KEY=xxx
PINECONE_INDEX=rag-prod
```

#### Graph Database
```env
NEO4J_URI=neo4j://neo4j.example.com:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=xxx
```

#### Search
```env
ELASTICSEARCH_HOST=es.example.com
ELASTICSEARCH_PORT=9200
```

### Runtime Configuration

See `config/settings.py` for all options:

```python
# Feature toggles
USE_SEMANTIC_CACHE=True
USE_GRAPHRAG=True
USE_MULTIMODAL_RETRIEVAL=True

# Rate limits
RATE_LIMIT_QUERIES_PER_MINUTE=100
RATE_LIMIT_TOKENS_PER_DAY=1000000

# Evaluation thresholds
RAGAS_THRESHOLD=0.7
```

### Tenant Configuration

Edit `config/tenant_config.py` to add tenant-specific overrides:

```python
{
    "acme-corp": {
        "max_documents": 100000,
        "max_queries_per_day": 50000,
        "enabled_retrievers": ["vector", "web"],
        "embedding_model": "text-embedding-3-large",
    }
}
```

### Intent Routing

Configure intent-based routing in `config/routing_table.py`:

```python
"factual_qa": {
    "retrievers": ["vector", "keyword", "graph"],
    "reranking_strategy": "cascade",
    "enable_web_search": False,
}
```

## Docker Compose Services

### Database Stack
- **PostgreSQL**: Document metadata
- **Redis**: Caching and session store
- **Qdrant**: Vector database
- **Neo4j**: Knowledge graph
- **Elasticsearch**: Full-text search
- **Chroma**: Dev vector store

### Starting Services
```bash
# Start all
docker-compose up -d

# Start specific services
docker-compose up -d postgres redis qdrant

# View logs
docker-compose logs -f qdrant
```

### Connection Strings

```python
# PostgreSQL
DATABASE_URL = "postgresql://user:pass@localhost:5432/rag_db"

# Redis
REDIS_URL = "redis://localhost:6379/0"

# Qdrant
QDRANT_URL = "http://localhost:6333"

# Neo4j
NEO4J_URI = "bolt://localhost:7687"
```

## Model Selection

### Embedding Models

```python
# Fast (default)
"text-embedding-3-small"  # 1536 dims

# Accurate
"text-embedding-3-large"  # 3072 dims

# Self-hosted
"BAAI/bge-base-en-v1.5"  # 768 dims
```

### LLM Models

```python
# Fast & cheap
"gpt-3.5-turbo"

# Balanced (recommended)
"gpt-4-turbo"

# Advanced reasoning
"claude-3-opus-20240229"
```

### Reranker Models

```python
# Fast (default)
"ms-marco-MiniLM-L-12-v2"

# Better quality
"BAAI/bge-reranker-large"

# API-based
"cohere-reranker"
```

## Performance Tuning

### Ingestion
```python
# Batch embedding
BATCH_SIZE = 32

# Chunk size
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

# Max workers
MAX_WORKERS = 4
```

### Retrieval
```python
# Top-k results
TOP_K = 10

# Retriever timeout
RETRIEVER_TIMEOUT_MS = 5000

# Fusion strategy
FUSION_METHOD = "rrf"  # or "weighted"
```

### Processing
```python
# Reranking cascade levels
RERANKING_LEVELS = [
    {"type": "bm25", "top_k": 50},
    {"type": "cross_encoder", "top_k": 20},
    {"type": "cohere", "top_k": 10},
]

# Compression
MAX_CONTEXT_TOKENS = 2000
```

### Caching
```python
# Memory cache size
L1_CACHE_SIZE = 1000

# Redis TTL
REDIS_TTL = 3600

# Semantic cache threshold
SEMANTIC_SIMILARITY_THRESHOLD = 0.95
```

## Observability Configuration

### Langfuse
```env
LANGFUSE_PUBLIC_KEY=xxx
LANGFUSE_SECRET_KEY=xxx
```

### OpenTelemetry
```env
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_METRICS_EXPORTER=otlp
```

### Prometheus
```env
PROMETHEUS_PUSHGATEWAY=localhost:9091
```

## Security Configuration

### RBAC
```python
# Require permission checks
ENFORCE_RBAC = True

# Role definitions
ROLES = {
    "admin": ["read", "write", "delete"],
    "user": ["read"],
}
```

### PII Protection
```python
# Enable PII detection
ENABLE_PII_DETECTION = True

# Redaction patterns
PII_PATTERNS = [
    "email",
    "phone",
    "ssn",
    "credit_card",
]
```

### Rate Limiting
```python
# Per-user limits
RATE_LIMIT_QUERIES_PER_MINUTE = 100

# Token budget
RATE_LIMIT_TOKENS_PER_DAY = 1000000
```

## Development vs Production

### Development
```env
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG
RAGAS_THRESHOLD=0.5
ENABLE_SHADOW_MODE=True
```

### Production
```env
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
RAGAS_THRESHOLD=0.8
ENABLE_SHADOW_MODE=False
```
