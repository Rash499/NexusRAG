from typing import Any

DEFAULT_GROUNDED_TEMPLATE = """
You are a grounded question-answering assistant for NexusRAG.

Answer the user's question using ONLY the supplied context.

If the context does not contain enough information, say:
"The available documents do not provide enough information to answer this question."

Do not invent facts. Always be accurate, concise, and helpful.

Cite the sources you use with [Source N] notation.

Context:
{context}

Question:
{question}

Answer:
""".strip()

def build_rag_prompt(question: str, points: list[Any]) -> str:
    """Build the grounded LLM prompt using retrieved documents."""
    context_parts = []

    for idx, point in enumerate(points, start=1):
        payload = point.payload or {}
        title = payload.get("title", "Unknown")
        text = payload.get("text", "")

        context_parts.append(
            f"[Source {idx}] {title}\n{text}"
        )

    context = "\n\n".join(context_parts) if context_parts else "No relevant documents found."

    return DEFAULT_GROUNDED_TEMPLATE.format(
        context=context,
        question=question,
    )
