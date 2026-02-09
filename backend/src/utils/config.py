from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Database
    database_url: str = "sqlite:///./questionnaire.db"
    
    # Celery Broker
    celery_broker_url: str = "sqla+sqlite:///./questionnaire.db"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Gemini
    google_api_key: str = ""
    embedding_model: str = "models/gemini-embedding-001"
    embedding_dimension: int = 3072
    
    # Document Storage
    upload_dir: str = "storage/documents"
    index_dir: str = "storage/indices"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions: list[str] = [".pdf", ".docx", ".xlsx", ".pptx"]
    
    # Chunking Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    min_chunk_size: int = 100
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
