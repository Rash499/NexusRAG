import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from ..config import settings
from ..rag.indexer import DocumentIndexer
from ..schemas import DirectIngestRequest, IngestResponse

router = APIRouter(prefix="/api/v1", tags=["Ingestion"])
indexer = DocumentIndexer()

@router.post("/ingest", response_model=IngestResponse)
async def ingest_corpus():
    """Ingest the local static corpus.json file into Qdrant."""
    corpus_path = Path(__file__).resolve().parent.parent.parent / "data" / "corpus.json"

    if not corpus_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Corpus file not found at: {corpus_path}",
        )

    try:
        documents = json.loads(corpus_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid corpus JSON: {exc}",
        ) from exc

    if not isinstance(documents, list):
        raise HTTPException(
            status_code=500,
            detail="corpus.json root must be a JSON array",
        )

    try:
        count = await indexer.index_documents(documents)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Document indexing failed: {exc}",
        ) from exc

    return IngestResponse(
        indexed=count,
        collection=settings.qdrant_collection,
        message=f"Successfully indexed {count} documents into {settings.qdrant_collection}",
    )

@router.post("/ingest/direct", response_model=IngestResponse)
async def ingest_direct(request: DirectIngestRequest):
    """Dynamically ingest arbitrary documents without rebuilding the file corpus."""
    if not request.documents:
        raise HTTPException(status_code=400, detail="Document list cannot be empty")

    docs = [doc.model_dump() for doc in request.documents]
    coll = request.collection or settings.qdrant_collection

    try:
        count = await indexer.index_documents(docs, collection_name=coll)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Direct indexing failed: {exc}") from exc

    return IngestResponse(
        indexed=count,
        collection=coll,
        message=f"Indexed {count} dynamic documents into {coll}",
    )
