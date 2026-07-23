"""Logging setup ≈ Logback config.

Plain stdlib logging here on purpose; module 14 upgrades to structlog
(structured JSON logs) for production.

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn app.main:app --reload   (from 11-project-architecture/)
"""

import logging


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )
