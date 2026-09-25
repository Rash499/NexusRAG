# NexusRAG: Enterprise Production RAG Platform (v2.0)

A modular, DevOps-first Retrieval-Augmented Generation (RAG) platform with full observability, real-time telemetry, dynamic ingestion, and token-streaming support:

- **React + Vite Frontend (v2.0)**: Modern knowledge console with tabbed interface, direct document insertion, parameter adjustment (top_k, min_similarity, token streaming), clipboard export, and real-time backend cluster health badges.
- **FastAPI Modular API (v2.0)**: Clean layered architecture separated into distinct domain packages (`clients`, `rag`, `routes`).
- **Sentence-Transformers Embedding Service**: Dedicated microservice for fast vector representations.
- **Qdrant Vector Database**: Production-grade vector storage with automatic collection provisioning and cosine semantic search.
- **Ollama LLM Engine**: Local grounded generation with citation matching (`[Source N]`).
- **Prometheus Metrics**: Built-in latency histograms (retrieval, LLM inference, total pipeline), similarity tracking, and query counters.
- **Docker Compose**: Containerized multi-service development setup.

---

## Architecture

```text
React (Vite Console)
  │
  ├───► FastAPI Modular API ──────► Ollama (llama3.2:3b)
  │       ├── routes (ingest, query, system)
  │       ├── rag (retriever, indexer, pipeline, prompt)
  │       └── clients (qdrant, embedding, ollama)
  │               │
  │               ├───► Embedding Service (all-MiniLM-L6-v2)
  │               └───► Qdrant Vector Store
  │
  └───────► Prometheus Metrics (/metrics)
```

---

## New Features & Enhancements in v2.0

### 1. Codebase Separation & Modular Architecture
- **Decomposed Large Files**: Separated monolithic `services.py` and `main.py` into dedicated, single-responsibility modules:
  - `api/app/clients/`: `embedding_client.py`, `ollama_client.py`, `qdrant_client_wrapper.py`.
  - `api/app/rag/`: `indexer.py`, `retriever.py`, `pipeline.py`, `prompt_builder.py`.
  - `api/app/routes/`: `ingest.py`, `query.py`, `system.py`.
- Full backwards-compatibility preserved for test runners and evaluation pipelines.

### 2. Frontend Enhancements
- **Dynamic Document Ingestion UI**: Ingest markdown or technical guides straight from the browser into Qdrant without restarting or manual corpus editing.
- **Live Infrastructure Diagnostics**: View real-time cluster status, vector counts, and connection health for Qdrant, Embedding Service, and Ollama.
- **Advanced Parameters Panel**: Customize Top-K chunk retrieval and similarity cutoff thresholds dynamically per query.
- **Token Streaming Support**: Stream response tokens directly for real-time interactive generation.
- **Recent Queries & Search History**: Save and recall prompt queries with 1 click.
- **Copy Answer & Evidence Filter**: One-click markdown copy and client-side filtering through retrieved context chunks.

### 3. Backend Enhancements
- **Dynamic Ingest Endpoint**: `POST /api/v1/ingest/direct` to vector-embed arbitrary documents on demand.
- **Cluster Diagnostics Endpoints**: `GET /api/v1/status` and `GET /api/v1/stats`.
- **Streaming Query Endpoint**: `POST /api/v1/query/stream` supporting chunked response streaming.

---

## Quick Start

### Requirements:
- Docker Desktop
- At least 8 GB RAM recommended

```bash
# Clone the repository
git clone <your-repository-url>
cd NexusRAG

# Launch all microservices
docker compose up -d --build
```

Pull the LLM model (first time only):
```bash
docker compose exec ollama ollama pull llama3.2:3b
```

Open in your browser:
- **Frontend Console**: [http://localhost:3000](http://localhost:3000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Qdrant Vector Dashboard**: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)
- **Prometheus Metrics**: [http://localhost:8000/metrics](http://localhost:8000/metrics)

---

## Running Automated Tests

### Backend Tests (Pytest)
```bash
cd api
pytest
```

### Frontend Tests (Vitest)
```bash
cd frontend
npm test
```

