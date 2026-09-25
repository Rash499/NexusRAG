import httpx
from ..config import settings

class EmbeddingClient:
    """Client for interacting with the external Sentence-Transformers embedding service."""

    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or settings.embedding_url).rstrip("/")
        self.timeout = timeout or settings.embedding_timeout_seconds

    async def get_embedding(self, text: str) -> list[float]:
        """Generate an embedding vector for a given piece of text."""
        if not text or not text.strip():
            raise ValueError("Cannot generate an embedding for empty text")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/embed",
                json={"text": text.strip()},
            )
            response.raise_for_status()
            data = response.json()

            if "embedding" not in data:
                raise ValueError("Embedding service response does not contain 'embedding'")

            vector = data["embedding"]
            if not isinstance(vector, list) or not vector:
                raise ValueError("Embedding service returned an invalid embedding")

            return vector

    async def check_health(self) -> dict:
        """Check status of embedding service."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/health")
                if res.status_code == 200:
                    return {"reachable": True, "details": res.json()}
                return {"reachable": False, "status_code": res.status_code}
        except Exception as exc:
            return {"reachable": False, "error": str(exc)}
