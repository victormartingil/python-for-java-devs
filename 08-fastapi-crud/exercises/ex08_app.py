"""The exercise app — module 08's tasks API with three features removed.

Same entry-point shape as 08-fastapi-crud/tasks_app.py. Nothing to implement
here — the exercises live in ex08_router.py / ex08_schemas.py / ex08_store.py.

    uv run pytest 08-fastapi-crud/exercises -v
"""

from ex08_router import router as tasks_router
from fastapi import FastAPI

app = FastAPI(title="Tasks API — module 08 exercises", version="0.8.1")
app.include_router(tasks_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
