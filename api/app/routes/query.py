from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ..rag.pipeline import RAGPipeline
from ..schemas import QueryRequest, QueryResponse

router = APIRouter(prefix="/api/v1", tags=["Query"])
pipeline = RAGPipeline()

@router.post("/query", response_model=QueryResponse)
async def query_corpus(request: QueryRequest):
    """Query knowledge base and synthesize a grounded response using Ollama."""
    try:
        result = await pipeline.answer_question(
            question=request.question,
            top_k=request.top_k,
            min_similarity=request.min_similarity,
            model=request.model,
        )
        return QueryResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Error querying RAG pipeline: {exc}",
        ) from exc

@router.post("/query/stream")
async def query_corpus_stream(request: QueryRequest):
    """Stream response tokens for interactive conversational experience."""
    async def event_generator():
        try:
            async for chunk in pipeline.answer_stream(
                question=request.question,
                top_k=request.top_k,
                min_similarity=request.min_similarity,
                model=request.model,
            ):
                yield chunk
        except Exception as exc:
            yield f"\n[Stream Error: {exc}]"

    return StreamingResponse(event_generator(), media_type="text/plain")
