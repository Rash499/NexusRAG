from prometheus_client import Counter, Histogram, Gauge

QUERY_COUNTER = Counter(
    "rag_queries_total",
    "Total RAG queries",
    ["status"],
)

QUERY_FAILURES = Counter(
    "rag_query_failures_total",
    "Failed RAG queries",
)

RETRIEVAL_LATENCY = Histogram(
    "rag_retrieval_latency_seconds",
    "Vector retrieval latency",
)

LLM_LATENCY = Histogram(
    "rag_llm_latency_seconds",
    "LLM generation latency",
)

TOTAL_LATENCY = Histogram(
    "rag_total_latency_seconds",
    "End-to-end RAG latency",
)

LOW_SIMILARITY = Counter(
    "rag_low_similarity_queries_total",
    "Queries where retrieved documents were below the similarity threshold",
)

AVG_SIMILARITY = Gauge(
    "rag_last_average_similarity",
    "Average similarity score for the latest query",
)
