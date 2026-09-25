from fastapi import APIRouter
from ..clients.embedding_client import EmbeddingClient
from ..clients.ollama_client import OllamaClient
from ..clients.qdrant_client_wrapper import QdrantClientWrapper
from ..config import settings
from ..schemas import CollectionStats, SystemStatusResponse

router = APIRouter(prefix="/api/v1", tags=["System"])

embedding_client = EmbeddingClient()
ollama_client = OllamaClient()
qdrant_wrapper = QdrantClientWrapper()

@router.get("/status", response_model=SystemStatusResponse)
async def system_status():
    """Returns connectivity and stats for Qdrant, Embedding, and Ollama services."""
    qdrant_info = await qdrant_wrapper.check_health()
    embedding_info = await embedding_client.check_health()
    llm_info = await ollama_client.check_health()
    stats_data = await qdrant_wrapper.get_collection_info()

    coll_stats = None
    if stats_data:
        coll_stats = CollectionStats(
            name=stats_data["name"],
            status=stats_data["status"],
            vectors_count=stats_data["vectors_count"],
            points_count=stats_data["points_count"],
        )

    all_reachable = (
        qdrant_info.get("reachable", False)
        and embedding_info.get("reachable", False)
        and llm_info.get("reachable", False)
    )

    return SystemStatusResponse(
        status="healthy" if all_reachable else "degraded",
        version="2.0.0",
        qdrant=qdrant_info,
        embedding_service=embedding_info,
        llm_service=llm_info,
        stats=coll_stats,
    )

@router.get("/stats")
async def collection_stats():
    """Retrieve detailed vector count and storage metrics for the active collection."""
    info = await qdrant_wrapper.get_collection_info()
    return {
        "collection": settings.qdrant_collection,
        "details": info or {"status": "not_created", "points_count": 0},
    }
