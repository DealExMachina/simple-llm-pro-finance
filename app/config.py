from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model: str = "DragonLLM/qwen3-8b-fin-v1.0"
    service_api_key: str | None = None
    log_level: str = "info"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields in .env


settings = Settings()


