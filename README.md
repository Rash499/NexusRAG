# Production RAG Platform

A DevOps-first Retrieval-Augmented Generation platform built with:

- React + Vite frontend
- FastAPI API
- Separate sentence-transformers embedding service
- Qdrant vector database
- Ollama LLM
- Docker Compose for local development
- RAG evaluation in CI
- Terraform for Azure infrastructure
- Kubernetes manifests for AKS
- GitHub Actions CI/CD
- Prometheus metrics + Azure Monitor/Log Analytics integration points

## Architecture

```text
React
  |
  v
FastAPI API ----> Ollama
  |
  +----> Embedding Service ----> Qdrant
  |
  +----> Prometheus metrics
```

## Quick start

Requirements:

- Docker Desktop
- Git
- At least 8 GB RAM recommended
- Ollama model access is easiest through the included Ollama container

```bash
git clone <your-repository-url>
cd production-rag-platform
docker compose up -d --build
```

Pull the default model:

```bash
docker compose exec ollama ollama pull llama3.2:3b
```

Open:

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- Qdrant: http://localhost:6333/dashboard
- Metrics: http://localhost:8000/metrics

## Index the sample corpus

```bash
curl -X POST http://localhost:8000/api/v1/ingest
```

Then ask questions from the web UI.

## Run tests

```bash
docker compose run --rm api pytest
docker compose run --rm embedding pytest
```

## Run evaluation

```bash
docker compose run --rm api python -m app.evaluation.run_eval
```

## Project phases

1. Local RAG
2. Docker Compose
3. RAG evaluation
4. CI/CD
5. Terraform
6. AKS
7. Monitoring
8. Security hardening

## Important production notes

The included Azure/Terraform and Kubernetes configurations are a production-oriented baseline, not a claim that every cloud security setting is complete for every environment. Before production use, review network ranges, identities, ingress certificates, storage classes, secrets, resource sizing, backup/restore, image signing, and organizational Azure policies.

Ollama is included for local development. For an AKS deployment, consider a managed LLM endpoint or a dedicated GPU-backed inference workload instead of placing a CPU-only Ollama container in a small general-purpose cluster.
