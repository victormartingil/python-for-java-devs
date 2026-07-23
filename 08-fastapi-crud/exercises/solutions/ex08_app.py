"""The exercise app — provided identically in exercises/ and solutions/.

(The solutions gate copies exercise files and shadows them with solutions;
this file has no stub, so both copies are the same.)
"""

from ex08_router import router as tasks_router
from fastapi import FastAPI

app = FastAPI(title="Tasks API — module 08 exercises", version="0.8.1")
app.include_router(tasks_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
