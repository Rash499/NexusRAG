from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "rag_documents"
    embedding_url: str = "http://localhost:8001"
    llm_base_url: str = "http://localhost:11434"
    llm_model: str = "llama3.2:3b"
    top_k: int = 5
    min_similarity: float = 0.25
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
    embedding_timeout_seconds: float = 60.0
    llm_timeout_seconds: float = 120.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

