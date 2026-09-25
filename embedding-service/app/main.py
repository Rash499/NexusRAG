import os
import threading
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

# FastEmbed stores its ONNX weights here. Point FASTEMBED_CACHE_PATH at a
# directory baked into the image so no download happens at runtime.
CACHE_DIR = os.getenv("FASTEMBED_CACHE_PATH") or None

app = FastAPI(
    title="RAG Embedding Service",
    version="2.0.0",
)

_engine: Any | None = None
_engine_lock = threading.Lock()


def get_engine() -> Any:
    """Build the shared FastEmbed ONNX engine once, lazily and thread-safe."""
    global _engine
    if _engine is None:
        with _engine_lock:
            if _engine is None:
                from fastembed import TextEmbedding

                _engine = TextEmbedding(
                    model_name=MODEL_NAME,
                    cache_dir=CACHE_DIR,
                )
    return _engine


def get_dimension() -> int:
    """Read the embedding size from the FastEmbed registry, probing if unknown."""
    for entry in get_engine().list_supported_models():
        if str(entry.get("model", "")).lower() == MODEL_NAME.lower():
            return int(entry["dim"])

    probe = next(iter(get_engine().embed(["dimension probe"])))
    return int(probe.shape[-1])


class EmbedRequest(BaseModel):
    text: str


class EmbedResponse(BaseModel):
    embedding: list[float]


class HealthResponse(BaseModel):
    status: str
    model: str
    dimension: int


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    try:
        return HealthResponse(
            status="healthy",
            model=MODEL_NAME,
            dimension=get_dimension(),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Embedding engine unavailable: {exc}",
        ) from exc


@app.post("/embed", response_model=EmbedResponse)
def embed(request: EmbedRequest) -> EmbedResponse:
    # Declared with `def` so FastAPI runs ONNX inference in its threadpool
    # instead of blocking the event loop.
    text = (request.text or "").strip()
    if not text:
        raise HTTPException(status_code=422, detail="Field 'text' must not be empty")

    try:
        vectors = list(get_engine().embed([text]))
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to generate embedding: {exc}",
        ) from exc

    if not vectors:
        raise HTTPException(status_code=503, detail="Embedding engine returned no vectors")

    return EmbedResponse(embedding=[float(value) for value in vectors[0].tolist()])
