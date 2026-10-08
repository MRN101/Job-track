"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "sqlite:///./data/jobpulse.db"

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # Frontend URL (for CORS)
    frontend_url: str = "http://localhost:3000"

    # Job Data Sources
    adzuna_app_id: Optional[str] = None
    adzuna_api_key: Optional[str] = None

    # LLM Configuration
    openai_api_key: Optional[str] = None
    llm_model: str = "gpt-4o-mini"
    llm_enabled: bool = False

    # Scheduling
    collection_schedule: str = "manual"

    # Logging
    log_level: str = "INFO"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the application settings (singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
