from contextlib import asynccontextmanager
from pathlib import Path
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from .config import settings
from .schemas import IngestResponse, QueryRequest, QueryResponse
from .services import index_documents, answer_question

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="Production RAG API",
    version="1.0.0",
    description="DevOps-first Retrieval-Augmented Generation API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/metrics", make_asgi_app())

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/v1/ingest", response_model=IngestResponse)
async def ingest():
    corpus_path = Path("/app/data/corpus.json")
    if not corpus_path.exists():
        raise HTTPException(status_code=404, detail="Corpus not found")

    documents = json.loads(corpus_path.read_text(encoding="utf-8"))
    count = await index_documents(documents)

    return {
        "indexed": count,
        "collection": settings.qdrant_collection,
        "message": "Documents indexed successfully",
    }

@app.post("/api/v1/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        return await answer_question(request.question, request.top_k)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
