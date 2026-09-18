from pydantic import BaseModel, Field

class IngestResponse(BaseModel):
    indexed: int
    collection: str
    message: str

class Source(BaseModel):
    id: str
    title: str
    text: str
    score: float

class QueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    top_k: int | None = Field(default=None, ge=1, le=20)

class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]
    retrieval_latency_ms: float
    llm_latency_ms: float
    total_latency_ms: float
    average_similarity: float
    success: bool
