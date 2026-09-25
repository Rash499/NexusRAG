from typing import Any
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from ..config import settings

class QdrantClientWrapper:
    """Encapsulates Qdrant vector database interactions."""

    def __init__(self, url: str | None = None, collection_name: str | None = None):
        self.url = url or settings.qdrant_url
        self.collection_name = collection_name or settings.qdrant_collection
        self._client = AsyncQdrantClient(url=self.url)

    @property
    def client(self) -> AsyncQdrantClient:
        return self._client

    async def ensure_collection(self, vector_size: int, collection_name: str | None = None) -> bool:
        """Create the Qdrant collection if it does not already exist."""
        coll = collection_name or self.collection_name
        exists = await self._client.collection_exists(coll)
        if not exists:
            await self._client.create_collection(
                collection_name=coll,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )
            return True
        return False

    async def upsert_points(self, points: list[PointStruct], collection_name: str | None = None):
        """Insert or update vector points in Qdrant."""
        coll = collection_name or self.collection_name
        return await self._client.upsert(
            collection_name=coll,
            points=points,
        )

    async def search(self, query_vector: list[float], limit: int, collection_name: str | None = None):
        """Query nearest neighbor points by vector."""
        coll = collection_name or self.collection_name
        exists = await self._client.collection_exists(coll)
        if not exists:
            return []

        result = await self._client.query_points(
            collection_name=coll,
            query=query_vector,
            limit=limit,
            with_payload=True,
        )
        return result.points

    async def get_collection_info(self, collection_name: str | None = None) -> dict[str, Any] | None:
        """Get collection metrics such as vector count and status."""
        coll = collection_name or self.collection_name
        try:
            exists = await self._client.collection_exists(coll)
            if not exists:
                return None
            info = await self._client.get_collection(coll)
            return {
                "name": coll,
                "status": str(info.status),
                "vectors_count": info.vectors_count or 0,
                "points_count": info.points_count or 0,
            }
        except Exception:
            return None

    async def check_health(self) -> dict:
        """Check whether Qdrant cluster is responsive."""
        try:
            collections = await self._client.get_collections()
            return {
                "reachable": True,
                "collections": [c.name for c in collections.collections],
            }
        except Exception as exc:
            return {"reachable": False, "error": str(exc)}
