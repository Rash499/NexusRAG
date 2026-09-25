import time
from typing import Any
from ..clients.embedding_client import EmbeddingClient
from ..clients.qdrant_client_wrapper import QdrantClientWrapper
from ..config import settings
from ..metrics import RETRIEVAL_LATENCY

class DocumentRetriever:
    """Handles query vectorization and semantic search against Qdrant."""

    def __init__(
        self,
        embedding_client: EmbeddingClient | None = None,
        qdrant_wrapper: QdrantClientWrapper | None = None,
    ):
        self.embedding_client = embedding_client or EmbeddingClient()
        self.qdrant_wrapper = qdrant_wrapper or QdrantClientWrapper()

    async def retrieve(
        self,
        question: str,
        top_k: int | None = None,
        collection_name: str | None = None,
    ) -> tuple[list[Any], float]:
        """Embed query and search vector store. Returns points and retrieval latency in seconds."""
        limit = top_k or settings.top_k
        started = time.perf_counter()

        vector = await self.embedding_client.get_embedding(question)
        points = await self.qdrant_wrapper.search(
            query_vector=vector,
            limit=limit,
            collection_name=collection_name,
        )

        latency = time.perf_counter() - started
        RETRIEVAL_LATENCY.observe(latency)
        return points, latency
