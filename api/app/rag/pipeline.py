from collections.abc import AsyncIterator
import time
from typing import Any
from ..clients.ollama_client import OllamaClient
from ..config import settings
from ..metrics import (
    AVG_SIMILARITY,
    LLM_LATENCY,
    LOW_SIMILARITY,
    QUERY_COUNTER,
    QUERY_FAILURES,
    TOTAL_LATENCY,
)
from .prompt_builder import build_rag_prompt
from .retriever import DocumentRetriever

class RAGPipeline:
    """Coordinates semantic retrieval, similarity filtering, prompt building, and response synthesis."""

    def __init__(
        self,
        retriever: DocumentRetriever | None = None,
        ollama_client: OllamaClient | None = None,
    ):
        self.retriever = retriever or DocumentRetriever()
        self.ollama = ollama_client or OllamaClient()

    async def answer_question(
        self,
        question: str,
        top_k: int | None = None,
        min_similarity: float | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """Execute complete question-answering workflow."""
        started = time.perf_counter()
        k = top_k or settings.top_k
        cutoff = min_similarity if min_similarity is not None else settings.min_similarity

        # 1. Retrieval
        points, retrieval_seconds = await self.retriever.retrieve(question, top_k=k)

        # 2. Similarity analysis
        scores = [float(p.score) for p in points] if points else []
        average_similarity = sum(scores) / len(scores) if scores else 0.0
        AVG_SIMILARITY.set(average_similarity)

        is_low_similarity = (not points) or (average_similarity < cutoff)
        if is_low_similarity:
            LOW_SIMILARITY.inc()

        # 3. Prompt Construction
        prompt = build_rag_prompt(question, points)

        # 4. LLM Generation
        try:
            llm_started = time.perf_counter()
            answer = await self.ollama.generate(prompt, model=model)
            llm_seconds = time.perf_counter() - llm_started
            LLM_LATENCY.observe(llm_seconds)
            QUERY_COUNTER.labels(status="success").inc()
        except Exception:
            QUERY_FAILURES.inc()
            QUERY_COUNTER.labels(status="error").inc()
            raise

        total_seconds = time.perf_counter() - started
        TOTAL_LATENCY.observe(total_seconds)

        # 5. Extract structured sources
        sources = []
        for p in points:
            payload = p.payload or {}
            sources.append({
                "id": str(p.id),
                "title": payload.get("title", "Unknown"),
                "text": payload.get("text", ""),
                "score": float(p.score),
                "source": payload.get("source"),
            })

        grounded = not is_low_similarity

        return {
            "answer": answer,
            "sources": sources,
            "retrieval_latency_ms": round(retrieval_seconds * 1000, 2),
            "llm_latency_ms": round(llm_seconds * 1000, 2),
            "total_latency_ms": round(total_seconds * 1000, 2),
            "average_similarity": round(average_similarity, 4),
            "success": True,
            "grounded": grounded,
        }

    async def answer_stream(
        self,
        question: str,
        top_k: int | None = None,
        min_similarity: float | None = None,
        model: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream answer tokens from Ollama while returning grounded context."""
        k = top_k or settings.top_k
        points, _ = await self.retriever.retrieve(question, top_k=k)
        prompt = build_rag_prompt(question, points)

        async for chunk in self.ollama.generate_stream(prompt, model=model):
            yield chunk
