from collections.abc import AsyncIterator
import json
import httpx
from ..config import settings

class OllamaClient:
    """Client for interacting with the Ollama inference server."""

    def __init__(self, base_url: str | None = None, model: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or settings.llm_base_url).rstrip("/")
        self.default_model = model or settings.llm_model
        self.timeout = timeout or settings.llm_timeout_seconds

    async def generate(self, prompt: str, model: str | None = None) -> str:
        """Send a prompt to Ollama and return the complete generated response."""
        chosen_model = model or self.default_model
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": chosen_model,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()

    async def generate_stream(self, prompt: str, model: str | None = None) -> AsyncIterator[str]:
        """Stream response tokens from Ollama as Server-Sent Events or raw text chunks."""
        chosen_model = model or self.default_model
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={
                    "model": chosen_model,
                    "prompt": prompt,
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("response", "")
                        if token:
                            yield token
                    except Exception:
                        continue

    async def check_health(self) -> dict:
        """Check status of Ollama server and list available models."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    models = [m.get("name") for m in res.json().get("models", [])]
                    return {"reachable": True, "models": models}
                return {"reachable": False, "status_code": res.status_code}
        except Exception as exc:
            return {"reachable": False, "error": str(exc)}
