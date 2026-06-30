from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/contract_analyzer"
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # AI / LLM
    openai_api_key: str = ""
    litellm_api_key: str = ""
    litellm_base_url: str = ""
    litellm_model: str = "gpt-4o"
    litellm_embedding_model: str = "text-embedding-3-large"
    embedding_model: str = "text-embedding-3-large"
    google_client_id: str = ""

    # Vector Store
    chroma_persist_dir: str = "./chroma_db"
    upload_dir: str = "./uploads"

    # File Upload
    max_file_size_mb: int = 20
    max_upload_size_mb: int = 50

    # Authentication
    jwt_secret_key: str = "change-this-to-a-random-256-bit-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60
    access_token_expire_minutes: int = 1440

    # CORS
    allowed_origins: str = "http://localhost:5173"

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
