"""The application entry point ≈ the @SpringBootApplication class.

Run the API:    uv run uvicorn tasks_app:app --reload   (from 08-fastapi-crud/)
                (--reload ≈ Spring Boot DevTools: restart on file change)
Swagger UI:     http://127.0.0.1:8000/docs       (≈ springdoc-openapi, zero config)
OpenAPI JSON:   http://127.0.0.1:8000/openapi.json

`tasks_app:app` means: module `tasks_app.py`, variable `app`.
"""

from fastapi import FastAPI
from tasks_router import router as tasks_router

app = FastAPI(title="Tasks API — module 08", version="0.8.0")
app.include_router(tasks_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
