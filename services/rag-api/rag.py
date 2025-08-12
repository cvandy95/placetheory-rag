import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

@dataclass
class RetrievedChunk:
    id: str
    text: str
    metadata: Dict[str, Any]
    distance: float

class RAG:
    def __init__(self, persist_path="chroma", collection_name="nuggets"):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(collection_name, metadata={"hnsw:space":"cosine"})
        self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.llm = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

    def _embed(self, texts: List[str]) -> List[List[float]]:
        return self.embedder.encode(texts, normalize_embeddings=True).tolist()

    def ingest_rows(self, rows: List[Dict[str, Any]]):
        ids = [r["id"] for r in rows]
        docs = [r["text"] for r in rows]
        metas = [{k:v for k,v in r.items() if k not in ("id","text")} for r in rows]
        embs = self._embed(docs)
        try: self.collection.delete(ids=ids)
        except Exception: pass
        self.collection.add(ids=ids, documents=docs, metadatas=metas, embeddings=embs)

    def retrieve(self, query: str, top_k=5, where: Optional[Dict[str, Any]] = None):
        q = self._embed([query])[0]
        res = self.collection.query(query_embeddings=[q], n_results=top_k, where=where or {})
        out = []
        for i, doc in enumerate(res["documents"][0]):
            out.append(RetrievedChunk(
                id=res["ids"][0][i], text=doc, metadata=res["metadatas"][0][i], distance=res["distances"][0][i]
            ))
        return out

    def _prompt(self, question: str, chunks: List[RetrievedChunk]):
        context = "\n".join([f"[{c.id}] {c.text}" for c in chunks]) or "NO CONTEXT"
        system = ("You are a careful analytics assistant. Answer ONLY from context. "
                  "Cite sources by their [ID]. If insufficient, say you lack data.")
        user = f"Question: {question}\n\nContext:\n{context}\n\nAnswer:"
        return system, user

    def generate(self, question: str, chunks: List[RetrievedChunk]):
        system, user = self._prompt(question, chunks)
        if not self.llm:
            return {"answer": "LLM not configured. Top facts:\n" + "\n".join([f"- {c.text} [source: {c.id}]" for c in chunks]),
                    "sources": [c.id for c in chunks]}
        resp = self.llm.chat.completions.create(model=OPENAI_MODEL, temperature=0.2,
            messages=[{"role":"system","content":system},{"role":"user","content":user}])
        return {"answer": resp.choices[0].message.content, "sources": [c.id for c in chunks]}
