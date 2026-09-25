import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.rag.prompt_builder import build_rag_prompt

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0"

def test_prompt_builder():
    class DummyPoint:
        def __init__(self, title, text):
            self.payload = {"title": title, "text": text}

    points = [
        DummyPoint("Doc 1", "Content about Azure."),
        DummyPoint("Doc 2", "Content about Docker."),
    ]
    prompt = build_rag_prompt("What is Azure?", points)
    assert "Doc 1" in prompt
    assert "Content about Azure." in prompt
    assert "What is Azure?" in prompt
    assert "[Source 1]" in prompt
    assert "[Source 2]" in prompt

def test_system_status():
    with patch("app.routes.system.qdrant_wrapper.check_health", new_callable=AsyncMock) as mock_qdrant, \
         patch("app.routes.system.embedding_client.check_health", new_callable=AsyncMock) as mock_embed, \
         patch("app.routes.system.ollama_client.check_health", new_callable=AsyncMock) as mock_ollama, \
         patch("app.routes.system.qdrant_wrapper.get_collection_info", new_callable=AsyncMock) as mock_info:

        mock_qdrant.return_value = {"reachable": True, "collections": ["rag_documents"]}
        mock_embed.return_value = {"reachable": True, "details": {"status": "healthy"}}
        mock_ollama.return_value = {"reachable": True, "models": ["llama3.2:3b"]}
        mock_info.return_value = {
            "name": "rag_documents",
            "status": "green",
            "vectors_count": 42,
            "points_count": 42,
        }

        response = client.get("/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["stats"]["points_count"] == 42
        assert data["stats"]["name"] == "rag_documents"

def test_query_validation():
    # Question too short
    response = client.post("/api/v1/query", json={"question": "a"})
    assert response.status_code == 422

    # Top k out of bounds
    response = client.post("/api/v1/query", json={"question": "What is Docker?", "top_k": 99})
    assert response.status_code == 422

def test_query_success_mock():
    with patch("app.routes.query.pipeline.answer_question", new_callable=AsyncMock) as mock_answer:
        mock_answer.return_value = {
            "answer": "Docker provides containerization.",
            "sources": [
                {"id": "1", "title": "Docker guide", "text": "Containers isolate apps", "score": 0.89, "source": "docker.md"}
            ],
            "retrieval_latency_ms": 12.5,
            "llm_latency_ms": 140.2,
            "total_latency_ms": 152.7,
            "average_similarity": 0.89,
            "success": True,
            "grounded": True,
        }

        response = client.post("/api/v1/query", json={"question": "What is Docker?"})
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Docker provides containerization."
        assert len(data["sources"]) == 1
        assert data["grounded"] is True

