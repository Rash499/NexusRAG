import logging
from typing import Any
from qdrant_client.models import PointStruct
from ..clients.embedding_client import EmbeddingClient
from ..clients.qdrant_client_wrapper import QdrantClientWrapper
from ..config import settings

logger = logging.getLogger(__name__)

class DocumentIndexer:
    """Handles parsing, batching, vectorization, and indexing of documents into Qdrant."""

    def __init__(
        self,
        embedding_client: EmbeddingClient | None = None,
        qdrant_wrapper: QdrantClientWrapper | None = None,
    ):
        self.embedding_client = embedding_client or EmbeddingClient()
        self.qdrant_wrapper = qdrant_wrapper or QdrantClientWrapper()

    async def index_documents(
        self,
        documents: list[dict[str, Any]],
        collection_name: str | None = None,
    ) -> int:
        """Vectorize documents and upsert into Qdrant vector database."""
        if not documents:
            return 0

        target_coll = collection_name or settings.qdrant_collection
        vectors = []

        for i, doc in enumerate(documents):
            text = doc.get("text", "").strip()
            if not text:
                logger.warning(f"Skipping empty document at index {i}")
                continue

            title = doc.get("title", f"Document {i + 1}")
            source = doc.get("source", title)
            doc_id = doc.get("id") or str(i + 1)

            vector = await self.embedding_client.get_embedding(text)

            vectors.append(
                PointStruct(
                    id=i + 1,  # Keep integer or string id compatible with Qdrant
                    vector=vector,
                    payload={
                        "doc_id": str(doc_id),
                        "title": title,
                        "text": text,
                        "source": source,
                    },
                )
            )

        if not vectors:
            return 0

        # Ensure collection exists with dynamic dimension of vectors
        await self.qdrant_wrapper.ensure_collection(
            vector_size=len(vectors[0].vector),
            collection_name=target_coll,
        )

        await self.qdrant_wrapper.upsert_points(
            points=vectors,
            collection_name=target_coll,
        )

        logger.info(f"Indexed {len(vectors)} documents into '{target_coll}'")
        return len(vectors)
