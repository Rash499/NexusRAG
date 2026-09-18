import os
from functools import lru_cache
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)

app = FastAPI(title="RAG Embedding Service", version="1.0.0")

@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer(MODEL_NAME)

class EmbedRequest(BaseModel):
    text: str

class EmbedResponse(BaseModel):
    embedding: list[float]

@app.get("/health")
def health():
    model = get_model()
    return {
        "status": "healthy",
        "model": MODEL_NAME,
        "dimension": model.get_sentence_embedding_dimension(),
    }

@app.post("/embed", response_model=EmbedResponse)
def embed(request: EmbedRequest):
    model = get_model()
    vector = model.encode(request.text, normalize_embeddings=True).tolist()
    return {"embedding": vector}
