"""Placeholder API entry point"""

from fastapi import FastAPI

app = FastAPI(title="RAG Production System")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/query")
async def query(query: str):
    """Process RAG query"""
    return {"response": "", "sources": []}

@app.get("/metrics")
async def metrics():
    """Get system metrics"""
    return {"latency_p99_ms": 0, "throughput_qps": 0}
