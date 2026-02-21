from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API
    APP_NAME: str = "Physical AI Book RAG API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    # CORS - Docusaurus book URL
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "https://YOUR_GITHUB_USERNAME.github.io",
    ]

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_DIMENSIONS: int = 1536

    # Qdrant Cloud
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION_NAME: str = "physical_ai_book"

    # Neon PostgreSQL
    DATABASE_URL: str  # postgresql+asyncpg://user:password@host/dbname

    # RAG settings
    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.7
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100


settings = Settings()
