from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    vllm_base_url: str = "http://localhost:8000/v1"
    model: str = "DragonLLM/LLM-Pro-Finance-Small"
    service_api_key: str | None = None
    log_level: str = "info"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


