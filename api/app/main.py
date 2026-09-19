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
    allow_origins=[
        x.strip()
        for x in settings.cors_origins.split(",")
        if x.strip()
    ],
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
    # Works when FastAPI is running directly from the Windows project
    # and also works when the project is mounted inside a container.
    corpus_path = Path(__file__).resolve().parent.parent / "data" / "corpus.json"

    if not corpus_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Corpus not found: {corpus_path}",
        )

    try:
        documents = json.loads(
            corpus_path.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid corpus JSON: {exc}",
        ) from exc

    if not isinstance(documents, list):
        raise HTTPException(
            status_code=500,
            detail="corpus.json must contain a JSON array",
        )

    try:
        count = await index_documents(documents)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Document indexing failed: {exc}",
        ) from exc

    return {
        "indexed": count,
        "collection": settings.qdrant_collection,
        "message": "Documents indexed successfully",
    }


@app.post("/api/v1/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        return await answer_question(
            request.question,
            request.top_k,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc