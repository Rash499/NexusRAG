# Interview story

## Problem

I wanted to demonstrate that a RAG application is not only an AI/retrieval
problem but also a software delivery and operations problem.

## Engineering decisions

- Separated embeddings from the API so embedding computation can scale independently.
- Used Qdrant for vector retrieval.
- Containerized every application component for environment consistency.
- Added retrieval evaluation to the delivery pipeline.
- Added Prometheus metrics for retrieval, LLM, total latency, errors, and similarity.
- Used Terraform to provision AKS, networking, ACR, and Log Analytics.
- Used Kubernetes manifests for repeatable deployment.
- Used OIDC for GitHub-to-Azure authentication rather than storing Azure client secrets.
- Added a security roadmap covering Key Vault, private networking, WAF, RBAC,
  image scanning, and Defender for Cloud.

## What I would improve next

- Hybrid BM25 + vector retrieval.
- Better chunking and document metadata.
- Reranking.
- Automated answer faithfulness evaluation.
- Authentication and authorization.
- Private AKS/ACR networking.
- Managed LLM endpoint.
- OpenTelemetry tracing.
- Blue/green or canary deployment.
- Automated rollback based on SLOs.
