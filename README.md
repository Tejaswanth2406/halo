<img width="1876" height="838" alt="image" src="https://github.com/user-attachments/assets/6af7f8c8-acfc-4eb9-a086-94aa5381bd87" />

# RAG Production System

Enterprise-grade Retrieval Augmented Generation (RAG) system with advanced features including multi-agent orchestration, comprehensive guardrails, and emerging evaluation benchmarks.

## 📋 Features

### Core RAG Pipeline (10 Layers)
- **L0**: Ingestion - Multi-format parsers, chunking strategies, embeddings
- **L1**: Guardrails - Input/output safety, auth, compliance
- **L2**: Query Pipeline - Understanding, rewriting, routing  
- **L3**: Retrieval - 7+ retriever types + fusion strategies
- **L4**: Processing - Filtering, reranking, compression
- **L5**: Memory - Short/long-term, working, isolation
- **L6**: Agent - ReAct reasoning, multi-agent, reflection
- **L7**: Output Safety - Grounding, hallucination detection
- **L8**: Cost Tracking - Token counting, budgets, optimization
- **L9**: Evaluation - Offline/online, A/B testing, diagnostics

### Emerging Benchmarks (2024+)
- 13 cutting-edge evaluation metrics including:
  - **Context Relevance Precision** - Reduces context noise
  - **Contextual Faithfulness Score** - Semantic drift detection
  - **Multi-Hop Reasoning Accuracy** - Agent reasoning quality
  - **Token Efficiency Ratio** - Cost optimization metric
  - **Adversarial Robustness Score** - Security testing
  - And 8 more advanced metrics!

### Infrastructure
- Async-first architecture with streaming support
- Multi-database support (Qdrant, Chroma, Pinecone, Neo4j, Elasticsearch)
- Advanced caching (L1 memory, L2 Redis, semantic)
- Circuit breaker + graceful degradation
- Comprehensive observability (Langfuse, OpenTelemetry)

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- API keys for LLM providers

### Installation

```bash
# Clone and setup
git clone <repo>
cd rag-production-system

# Copy environment
cp .env.example .env
# Edit .env with your API keys

# Install dependencies
make install

# Start infrastructure
make docker-up

# Run tests
make test
```

### Development

```bash
# Setup dev environment
make dev

# Run linting
make lint

# Format code
make format

# Run with coverage
make test-coverage
```

## 📊 Evaluation

```bash
# Run RAGAS evaluation
make eval

# Run specific benchmark
python -m benchmarks.emerging.context_relevance_precision

# Generate report
python scripts/generate_benchmark_report.py
```

## 📚 Documentation

- [Architecture Guide](docs/architecture.md)
- [Configuration](docs/configuration.md)
- [API Reference](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [Benchmark Guide](docs/benchmarks.md)

## 🧪 Testing

```bash
# Unit tests
make test-unit

# Integration tests
make test-integration

# Adversarial tests
pytest tests/adversarial/

# Regression tests
python mlops/ci/regression_tests.py
```

## 🔒 Security

- Input validation and injection detection
- Output grounding verification
- PII detection and scrubbing
- Rate limiting
- RBAC with tenant isolation
- Adversarial query defense

## 📈 Monitoring & Observability

- Real-time query tracing with Langfuse
- OpenTelemetry integration
- Prometheus metrics
- Quality regression alerts
- Layer-wise bottleneck detection

## 🎯 Key Differentiators

1. **13 Emerging Benchmarks** - Beyond RAGAS, includes practical production metrics
2. **Multi-Agent System** - Specialized agents for retrieval, reasoning, verification
3. **Comprehensive Guardrails** - 15+ safety mechanisms for production reliability
4. **Cost Optimization** - Token tracking, budget control, model routing
5. **Enterprise Ready** - Audit trails, multi-tenancy, compliance features

## 📝 Benchmarks Overview

| Benchmark | Type | Use Case |
|-----------|------|----------|
| Context Relevance Precision | Output Quality | Reduce token waste |
| Contextual Faithfulness Score | Accuracy | Prevent semantic drift |
| Multi-Hop Reasoning Accuracy | Reasoning | Multi-step queries |
| RAG Diversity | Coverage | Source triangulation |
| Latency-Quality Tradeoff | SLO Optimization | Speed vs accuracy |
| Adversarial Robustness | Security | Attack resistance |
| Token Efficiency Ratio | Cost | $/quality ratio |

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 License

MIT License - See [LICENSE](LICENSE)

## 🔗 References

- RAGAS: [Es et al. 2023](https://arxiv.org/abs/2309.15217)
- GraphRAG: [Edge et al. 2024](https://arxiv.org/abs/2404.16130)
- ColPali: [Faysse et al. 2024](https://arxiv.org/abs/2407.01449)
- LLMLingua: [Jiang et al. 2023](https://arxiv.org/abs/2310.05033)

## 📞 Support

- GitHub Issues: [Report bugs](../../issues)
- Discussions: [Ask questions](../../discussions)
- Email: team@example.com
