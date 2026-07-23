"""Typed configuration ≈ application.yml + @ConfigurationProperties.

pydantic-settings reads environment variables (and a local .env file) into a
validated model. Missing/invalid config fails fast at startup — like Spring's
relaxed binding + validation, with types.

Copy .env.example to .env for local overrides. .env is gitignored repo-wide.

Run the API:  uv run uvicorn secureapp.main:app --reload   (from 09-fastapi-pro-di-auth-config/)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Field names map to env vars case-insensitively: secret_key <- SECRET_KEY.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ⚠️ Default is a DEV-ONLY value so the demo runs with zero setup.
    # In production SECRET_KEY must come from the environment / a secret manager.
    secret_key: str = "dev-only-insecure-secret-change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    # JSON array in .env, e.g. CORS_ORIGINS='["http://localhost:3000"]'
    cors_origins: list[str] = ["http://localhost:3000"]
