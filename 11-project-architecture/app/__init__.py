"""app — the tasks API at production structure: layered, organized by domain.

The Python/FastAPI answer to "where is my hexagonal architecture?" — see README.

Setup (from 11-project-architecture/):
  docker compose up -d
  uv run alembic upgrade head
  uv run uvicorn app.main:app --reload
Swagger UI: http://127.0.0.1:8000/docs
"""
