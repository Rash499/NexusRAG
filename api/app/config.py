from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "rag_documents"
    embedding_url: str = "http://localhost:8001"
    llm_base_url: str = "http://localhost:11434"
    llm_model: str = "llama3.2:3b"
    top_k: int = 5
    min_similarity: float = 0.25
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
