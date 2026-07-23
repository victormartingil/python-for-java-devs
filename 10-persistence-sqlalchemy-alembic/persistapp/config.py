"""Settings — same pattern as module 09, here for the database URL.

DATABASE_URL env var (or .env) overrides the default, which matches
docker-compose.yml in this directory.

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn persistapp.main:app --reload   (from 10-persistence-sqlalchemy-alembic/)
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Note the driver in the URL: +asyncpg = async driver (≈ choosing the JDBC driver).
    database_url: str = "postgresql+asyncpg://tasks:tasks@localhost:5432/tasks"


@lru_cache
def get_settings() -> Settings:
    return Settings()
