"""Application configuration using Pydantic settings."""

from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    Supports loading from .env file with UTF-8 encoding.
    All settings can be overridden via environment variables.
    """
    
    model: str = Field(
        default="DragonLLM/Qwen-Open-Finance-R-8B",
        description="Hugging Face model identifier"
    )
    service_api_key: str | None = Field(
        default=None,
        description="Optional API key for authentication (SERVICE_API_KEY env var)"
    )
    log_level: Literal["debug", "info", "warning", "error"] = Field(
        default="info",
        description="Logging level"
    )
    force_model_reload: bool = Field(
        default=False,
        description="Force model reload from Hugging Face, bypassing cache (FORCE_MODEL_RELOAD env var)"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


