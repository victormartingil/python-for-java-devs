"""persistapp — the tasks API persisted in real PostgreSQL.

SQLAlchemy 2.0 (async) + asyncpg + Alembic migrations.

Setup (from 10-persistence-sqlalchemy-alembic/):
  docker compose up -d                 # PostgreSQL 16
  uv run alembic upgrade head          # ≈ Flyway migrate
  uv run uvicorn persistapp.main:app --reload
Swagger UI: http://127.0.0.1:8000/docs
"""
