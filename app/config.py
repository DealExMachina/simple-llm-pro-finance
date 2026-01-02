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
    environment: Literal["development", "staging", "production"] = Field(
        default="production",
        description="Environment name for Logfire (ENVIRONMENT env var)"
    )
    enable_langfuse: bool = Field(
        default=True,
        description="Enable Langfuse observability (ENABLE_LANGFUSE env var)"
    )
    langfuse_public_key: str = Field(
        default="",
        description="Langfuse public key (LANGFUSE_PUBLIC_KEY env var)"
    )
    langfuse_secret_key: str = Field(
        default="",
        description="Langfuse secret key (LANGFUSE_SECRET_KEY env var)"
    )
    langfuse_host: str = Field(
        default="https://cloud.langfuse.com",
        description="Langfuse host URL (LANGFUSE_HOST env var)"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


