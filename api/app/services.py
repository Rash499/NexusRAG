"""
Backward compatibility layer for existing tests, scripts, and evaluation modules.
Delegates to the modular rag package and clients.
"""
import time
from typing import Any
from .clients.embedding_client import EmbeddingClient
from .clients.ollama_client import OllamaClient
from .clients.qdrant_client_wrapper import QdrantClientWrapper
from .rag.indexer import DocumentIndexer
from .rag.retriever import DocumentRetriever
from .rag.pipeline import RAGPipeline
from .rag.prompt_builder import build_rag_prompt
from .config import settings

_embedding_client = EmbeddingClient()
_ollama_client = OllamaClient()
_qdrant_wrapper = QdrantClientWrapper()
_retriever = DocumentRetriever(_embedding_client, _qdrant_wrapper)
_indexer = DocumentIndexer(_embedding_client, _qdrant_wrapper)
_pipeline = RAGPipeline(_retriever, _ollama_client)

qdrant = _qdrant_wrapper.client

async def embedding(text: str) -> list[float]:
    return await _embedding_client.get_embedding(text)

async def ensure_collection(vector_size: int):
    return await _qdrant_wrapper.ensure_collection(vector_size)

async def index_documents(documents: list[dict[str, Any]]) -> int:
    return await _indexer.index_documents(documents)

async def retrieve(question: str, top_k: int):
    return await _retriever.retrieve(question, top_k=top_k)

def build_prompt(question: str, points) -> str:
    return build_rag_prompt(question, points)

async def generate(prompt: str):
    started = time.perf_counter()
    ans = await _ollama_client.generate(prompt)
    latency = time.perf_counter() - started
    return ans, latency

async def answer_question(question: str, top_k: int | None = None):
    return await _pipeline.answer_question(question, top_k=top_k)
