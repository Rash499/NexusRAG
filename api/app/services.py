import time
from typing import Any
import httpx
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from .config import settings
from .metrics import (
    AVG_SIMILARITY,
    LLM_LATENCY,
    LOW_SIMILARITY,
    QUERY_COUNTER,
    QUERY_FAILURES,
    RETRIEVAL_LATENCY,
    TOTAL_LATENCY,
)

qdrant = AsyncQdrantClient(url=settings.qdrant_url)

async def embedding(text: str) -> list[float]:
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{settings.embedding_url}/embed",
            json={"text": text},
        )
        response.raise_for_status()
        return response.json()["embedding"]

async def ensure_collection(vector_size: int):
    exists = await qdrant.collection_exists(settings.qdrant_collection)
    if not exists:
        await qdrant.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

async def index_documents(documents: list[dict[str, Any]]) -> int:
    if not documents:
        return 0

    vectors = []
    for i, doc in enumerate(documents):
        vector = await embedding(doc["text"])
        vectors.append(
            PointStruct(
                id=i + 1,
                vector=vector,
                payload={
                    "title": doc["title"],
                    "text": doc["text"],
                    "source": doc.get("source", doc["title"]),
                },
            )
        )

    await ensure_collection(len(vectors[0].vector))
    await qdrant.upsert(
        collection_name=settings.qdrant_collection,
        points=vectors,
    )
    return len(vectors)

async def retrieve(question: str, top_k: int):
    started = time.perf_counter()
    vector = await embedding(question)

    exists = await qdrant.collection_exists(settings.qdrant_collection)
    if not exists:
        return [], (time.perf_counter() - started)

    result = await qdrant.query_points(
        collection_name=settings.qdrant_collection,
        query=vector,
        limit=top_k,
        with_payload=True,
    )
    latency = time.perf_counter() - started
    return result.points, latency

def build_prompt(question: str, points) -> str:
    context_parts = []
    for idx, point in enumerate(points, start=1):
        payload = point.payload or {}
        context_parts.append(
            f"[Source {idx}] {payload.get('title', 'Unknown')}\n"
            f"{payload.get('text', '')}"
        )

    context = "\n\n".join(context_parts)

    return f"""You are a grounded question-answering assistant.

Answer the user's question using ONLY the supplied context.
If the context does not contain enough information, say that the available
documents do not provide enough information.
Do not invent facts.
Cite sources using [Source N] notation.

Context:
{context}

Question:
{question}

Answer:"""

async def generate(prompt: str):
    started = time.perf_counter()
    async with httpx.AsyncClient(timeout=180) as client:
        response = await client.post(
            f"{settings.llm_base_url}/api/generate",
            json={
                "model": settings.llm_model,
                "prompt": prompt,
                "stream": False,
            },
        )
        response.raise_for_status()
        answer = response.json().get("response", "").strip()
    return answer, time.perf_counter() - started

async def answer_question(question: str, top_k: int | None = None):
    started = time.perf_counter()
    k = top_k or settings.top_k

    points, retrieval_seconds = await retrieve(question, k)
    RETRIEVAL_LATENCY.observe(retrieval_seconds)

    scores = [float(p.score) for p in points]
    average_similarity = sum(scores) / len(scores) if scores else 0.0
    AVG_SIMILARITY.set(average_similarity)

    if not points or average_similarity < settings.min_similarity:
        LOW_SIMILARITY.inc()

    prompt = build_prompt(question, points)

    try:
        answer, llm_seconds = await generate(prompt)
    except Exception:
        QUERY_FAILURES.inc()
        QUERY_COUNTER.labels(status="error").inc()
        raise

    LLM_LATENCY.observe(llm_seconds)
    total_seconds = time.perf_counter() - started
    TOTAL_LATENCY.observe(total_seconds)
    QUERY_COUNTER.labels(status="success").inc()

    sources = []
    for p in points:
        payload = p.payload or {}
        sources.append({
            "id": str(p.id),
            "title": payload.get("title", "Unknown"),
            "text": payload.get("text", ""),
            "score": float(p.score),
        })

    return {
        "answer": answer,
        "sources": sources,
        "retrieval_latency_ms": round(retrieval_seconds * 1000, 2),
        "llm_latency_ms": round(llm_seconds * 1000, 2),
        "total_latency_ms": round(total_seconds * 1000, 2),
        "average_similarity": round(average_similarity, 4),
        "success": True,
    }
