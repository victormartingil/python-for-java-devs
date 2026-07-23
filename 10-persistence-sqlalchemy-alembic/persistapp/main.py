"""App assembly.

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn persistapp.main:app --reload   (from 10-persistence-sqlalchemy-alembic/)
Swagger UI: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

from persistapp.router import router as tasks_router

app = FastAPI(title="Tasks API — module 10 (PostgreSQL)", version="0.10.0")
app.include_router(tasks_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
