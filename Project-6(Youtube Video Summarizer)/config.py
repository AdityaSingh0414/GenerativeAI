
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    max_tokens_per_chunk: int = 1800
    max_concurrent_requests: int = 4

    max_retries: int = 4
    retry_min_wait_seconds: float = 1.0
    retry_max_wait_seconds: float = 20.0

    cache_enabled: bool = True
    cache_db_path: str = "cache/summarizer_cache.sqlite3"

    qa_top_k: int = 4


settings = Settings()   