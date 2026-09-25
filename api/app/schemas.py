from pydantic import BaseModel, Field
from typing import Any

class IngestResponse(BaseModel):
    indexed: int
    collection: str
    message: str

class Source(BaseModel):
    id: str
    title: str
    text: str
    score: float
    source: str | None = None

class QueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    top_k: int | None = Field(default=None, ge=1, le=20)
    stream: bool = Field(default=False, description="Whether to stream the answer")
    min_similarity: float | None = Field(default=None, ge=0.0, le=1.0)
    model: str | None = Field(default=None, description="Optional LLM model override")

class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]
    retrieval_latency_ms: float
    llm_latency_ms: float
    total_latency_ms: float
    average_similarity: float
    success: bool
    grounded: bool = True

class DocumentItem(BaseModel):
    id: str | None = None
    title: str
    text: str
    source: str | None = None

class DirectIngestRequest(BaseModel):
    documents: list[DocumentItem]
    collection: str | None = None

class CollectionStats(BaseModel):
    name: str
    status: str
    vectors_count: int
    points_count: int

class SystemStatusResponse(BaseModel):
    status: str
    version: str
    qdrant: dict[str, Any]
    embedding_service: dict[str, Any]
    llm_service: dict[str, Any]
    stats: CollectionStats | None = None

