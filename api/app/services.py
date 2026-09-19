import time
from typing import Any

import httpx
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

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


# ---------------------------------------------------------
# Qdrant client
# ---------------------------------------------------------

qdrant = AsyncQdrantClient(
    url=settings.qdrant_url
)


# ---------------------------------------------------------
# Embedding service
# ---------------------------------------------------------

async def embedding(text: str) -> list[float]:
    """
    Generate an embedding using the embedding service.
    """

    if not text or not text.strip():
        raise ValueError("Cannot generate an embedding for empty text")

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{settings.embedding_url}/embed",
            json={"text": text},
        )

        response.raise_for_status()

        data = response.json()

        if "embedding" not in data:
            raise ValueError(
                "Embedding service response does not contain 'embedding'"
            )

        vector = data["embedding"]

        if not isinstance(vector, list) or not vector:
            raise ValueError(
                "Embedding service returned an invalid embedding"
            )

        return vector


# ---------------------------------------------------------
# Qdrant collection
# ---------------------------------------------------------

async def ensure_collection(vector_size: int):
    """
    Create the Qdrant collection if it does not already exist.
    """

    exists = await qdrant.collection_exists(
        settings.qdrant_collection
    )

    if not exists:
        await qdrant.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )

        print(
            f"Created Qdrant collection: "
            f"{settings.qdrant_collection}"
        )


# ---------------------------------------------------------
# Document indexing
# ---------------------------------------------------------

async def index_documents(
    documents: list[dict[str, Any]]
) -> int:
    """
    Generate embeddings for all documents and store them in Qdrant.
    """

    if not documents:
        return 0

    vectors = []

    for i, doc in enumerate(documents):
        text = doc.get("text", "").strip()

        if not text:
            print(
                f"Skipping empty document at index {i}"
            )
            continue

        title = doc.get(
            "title",
            f"Document {i + 1}",
        )

        source = doc.get(
            "source",
            title,
        )

        print(
            f"Embedding document {i + 1}/{len(documents)}: "
            f"{title}"
        )

        vector = await embedding(text)

        vectors.append(
            PointStruct(
                id=i + 1,
                vector=vector,
                payload={
                    "title": title,
                    "text": text,
                    "source": source,
                },
            )
        )

    if not vectors:
        return 0

    # Create collection using the actual embedding dimension.
    await ensure_collection(
        len(vectors[0].vector)
    )

    await qdrant.upsert(
        collection_name=settings.qdrant_collection,
        points=vectors,
    )

    print(
        f"Indexed {len(vectors)} documents into "
        f"Qdrant collection "
        f"'{settings.qdrant_collection}'"
    )

    return len(vectors)


# ---------------------------------------------------------
# Retrieval
# ---------------------------------------------------------

async def retrieve(
    question: str,
    top_k: int,
):
    """
    Embed the question and retrieve the most relevant
    documents from Qdrant.
    """

    started = time.perf_counter()

    vector = await embedding(question)

    exists = await qdrant.collection_exists(
        settings.qdrant_collection
    )

    if not exists:
        latency = time.perf_counter() - started

        print(
            f"Qdrant collection "
            f"'{settings.qdrant_collection}' "
            f"does not exist"
        )

        return [], latency

    result = await qdrant.query_points(
        collection_name=settings.qdrant_collection,
        query=vector,
        limit=top_k,
        with_payload=True,
    )

    latency = time.perf_counter() - started

    print(
        f"Retrieved {len(result.points)} points "
        f"from Qdrant"
    )

    for point in result.points:
        payload = point.payload or {}

        print(
            f"  - {payload.get('title', 'Unknown')} "
            f"(score={point.score:.4f})"
        )

    return result.points, latency


# ---------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------

def build_prompt(
    question: str,
    points,
) -> str:
    """
    Build the grounded LLM prompt using retrieved documents.
    """

    context_parts = []

    for idx, point in enumerate(
        points,
        start=1,
    ):
        payload = point.payload or {}

        title = payload.get(
            "title",
            "Unknown",
        )

        text = payload.get(
            "text",
            "",
        )

        context_parts.append(
            f"[Source {idx}] {title}\n"
            f"{text}"
        )

    context = "\n\n".join(
        context_parts
    )

    return f"""
You are a grounded question-answering assistant.

Answer the user's question using ONLY the supplied context.

If the context does not contain enough information, say:

"The available documents do not provide enough information to answer this question."

Do not invent facts.

Cite the sources you use with [Source N] notation.

Context:
{context}

Question:
{question}

Answer:
""".strip()


# ---------------------------------------------------------
# Ollama / LLM generation
# ---------------------------------------------------------

async def generate(
    prompt: str,
):
    """
    Send the grounded prompt to Ollama.
    """

    started = time.perf_counter()

    async with httpx.AsyncClient(
        timeout=180
    ) as client:

        response = await client.post(
            f"{settings.llm_base_url}/api/generate",
            json={
                "model": settings.llm_model,
                "prompt": prompt,
                "stream": False,
            },
        )

        response.raise_for_status()

        data = response.json()

        answer = data.get(
            "response",
            "",
        ).strip()

    latency = time.perf_counter() - started

    return answer, latency


# ---------------------------------------------------------
# Main RAG question-answering flow
# ---------------------------------------------------------

async def answer_question(
    question: str,
    top_k: int | None = None,
):
    """
    Complete RAG pipeline:

    Question
        ↓
    Embedding
        ↓
    Qdrant retrieval
        ↓
    Grounded prompt
        ↓
    Ollama
        ↓
    Answer + sources
    """

    started = time.perf_counter()

    k = top_k or settings.top_k

    # -----------------------------------------------------
    # Retrieval
    # -----------------------------------------------------

    points, retrieval_seconds = await retrieve(
        question,
        k,
    )

    RETRIEVAL_LATENCY.observe(
        retrieval_seconds
    )

    # -----------------------------------------------------
    # Similarity calculation
    # -----------------------------------------------------

    scores = [
        float(point.score)
        for point in points
    ]

    average_similarity = (
        sum(scores) / len(scores)
        if scores
        else 0.0
    )

    AVG_SIMILARITY.set(
        average_similarity
    )

    if (
        not points
        or average_similarity
        < settings.min_similarity
    ):
        LOW_SIMILARITY.inc()

    # -----------------------------------------------------
    # Build grounded prompt
    # -----------------------------------------------------

    prompt = build_prompt(
        question,
        points,
    )

    # -----------------------------------------------------
    # Generate answer
    # -----------------------------------------------------

    try:
        answer, llm_seconds = await generate(
            prompt
        )

    except Exception:
        QUERY_FAILURES.inc()
        QUERY_COUNTER.labels(
            status="error"
        ).inc()

        raise

    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

    LLM_LATENCY.observe(
        llm_seconds
    )

    total_seconds = (
        time.perf_counter()
        - started
    )

    TOTAL_LATENCY.observe(
        total_seconds
    )

    QUERY_COUNTER.labels(
        status="success"
    ).inc()

    # -----------------------------------------------------
    # Sources
    # -----------------------------------------------------

    sources = []

    for point in points:
        payload = point.payload or {}

        sources.append(
            {
                "id": str(point.id),
                "title": payload.get(
                    "title",
                    "Unknown",
                ),
                "text": payload.get(
                    "text",
                    "",
                ),
                "score": float(
                    point.score
                ),
            }
        )

    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return {
        "answer": answer,
        "sources": sources,
        "retrieval_latency_ms": round(
            retrieval_seconds * 1000,
            2,
        ),
        "llm_latency_ms": round(
            llm_seconds * 1000,
            2,
        ),
        "total_latency_ms": round(
            total_seconds * 1000,
            2,
        ),
        "average_similarity": round(
            average_similarity,
            4,
        ),
        "success": True,
    }