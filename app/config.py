from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model: str = "DragonLLM/qwen3-8b-fin-v1.0"
    service_api_key: str | None = None
    log_level: str = "info"
    force_model_reload: bool = False  # Set FORCE_MODEL_RELOAD=true to bypass cache on startup

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


