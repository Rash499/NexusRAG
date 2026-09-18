# Architecture

## Request path

1. Browser sends a question to FastAPI.
2. FastAPI requests an embedding from the embedding service.
3. The embedding is queried against Qdrant.
4. Retrieved chunks are assembled into a constrained prompt.
5. Ollama generates an answer.
6. FastAPI returns the answer, sources, similarity, and latency metrics.
7. Prometheus-compatible metrics expose operational data.

## Scaling

The API and embedding service are stateless and can scale horizontally.

Qdrant is stateful and requires persistent storage and a deliberate HA/backup
strategy for production.

LLM inference is separated from the API so it can later be replaced by a
managed endpoint or a GPU-backed inference service.

## Failure handling

- Missing corpus: ingestion returns HTTP 404.
- LLM/vector/embedding dependency errors: query returns HTTP 502.
- Low similarity: the request still reaches the LLM, but the application records
  a low-similarity metric and the prompt instructs the model not to invent facts.
- Health endpoints support Kubernetes probes.
