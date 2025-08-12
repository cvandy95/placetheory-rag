import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from rag import RAG

load_dotenv()
app = FastAPI(title="RAG Demo")
origins = os.getenv("CORS_ORIGINS","http://localhost:5500").split(",")
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in origins], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

rag = RAG(persist_path="chroma", collection_name="nuggets")

class ChatRequest(BaseModel):
    question: str
    where: Optional[Dict[str, Any]] = None
    top_k: int = 5

class IngestRow(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any] = {}

class IngestRequest(BaseModel):
    rows: List[IngestRow]

@app.get("/health")
def health(): return {"status":"ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    chunks = rag.retrieve(req.question, top_k=req.top_k, where=req.where)
    return rag.generate(req.question, chunks)

@app.post("/ingest")
def ingest(req: IngestRequest):
    rows = [{"id":r.id, "text":r.text, **(r.metadata or {})} for r in req.rows]
    rag.ingest_rows(rows)
    return {"ingested": len(rows)}
