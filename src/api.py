"""API entry point for the Core MVP RAG System"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import chromadb

from src.ingestion.parsers.pdf_parser import PDFParser
from src.ingestion.chunking.semantic_chunker import SemanticChunker
from src.ingestion.embedding.model_manager import EmbeddingModelManager
from src.retrieval.vector.chroma_retriever import ChromaRetriever

app = FastAPI(title="RAG Production System - Core MVP")

# Initialize core components
embedding_manager = EmbeddingModelManager()
chunker = SemanticChunker()
pdf_parser = PDFParser()

# Initialize ChromaDB (local ephemeral for MVP)
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="documents")
retriever = ChromaRetriever(collection)

class IngestRequest(BaseModel):
    file_path: str

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

@app.get("/health")
async def health():
    return {"status": "ok", "active_embedding_model": embedding_manager.active_model}

@app.post("/ingest")
async def ingest_document(req: IngestRequest):
    """Ingest a PDF document into the local ChromaDB vector store."""
    try:
        # 1. Parse PDF
        pages = pdf_parser.parse(req.file_path)
        if not pages:
            raise HTTPException(status_code=400, detail="Failed to parse PDF or file is empty.")
        
        # 2. Extract and Chunk text
        full_text = "\n\n".join([p.text for p in pages])
        chunks = chunker.chunk(full_text)
        
        # 3. Embed chunks
        texts = [c["content"] for c in chunks]
        embeddings = embedding_manager.embed_batch(texts)
        
        # 4. Index in ChromaDB
        ids = [c["chunk_id"] for c in chunks]
        metadatas = [{"chunk_index": c["chunk_index"], "source": req.file_path} for c in chunks]
        
        collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        return {"status": "success", "chunks_indexed": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query(req: QueryRequest):
    """Process RAG query and retrieve relevant context."""
    try:
        # 1. Embed query
        query_emb = embedding_manager.embed(req.query)
        
        # 2. Retrieve top-k chunks
        results = await retriever.retrieve(query_emb, k=req.top_k)
        
        # 3. Return context (In Phase 2, this will be passed to an LLM/Agent)
        contexts = [r["document"] for r in results]
        
        # Stubbed Generation (To be replaced with LLM/Agent pipeline)
        response_text = "Based on the context retrieved, here is the information:\n\n" + "\n".join(contexts)
        
        return {
            "query": req.query,
            "response": response_text,
            "sources": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
