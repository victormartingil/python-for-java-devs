"""Typed settings ≈ application.yml + @ConfigurationProperties (module 09 pattern).

DATABASE_URL / SECRET_KEY env vars (or .env) override the dev defaults;
the defaults match docker-compose.yml in this directory.

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn app.main:app --reload   (from 11-project-architecture/)
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://tasks:tasks@localhost:5432/tasks"
    # ⚠️ DEV-ONLY default so the demo runs with zero setup — set SECRET_KEY for real.
    secret_key: str = "dev-only-insecure-secret-change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


@lru_cache  # singleton bean
def get_settings() -> Settings:
    return Settings()
