"""App assembly ≈ the @SpringBootApplication class + WebMvcConfigurer.

Run the API:  uv run uvicorn secureapp.main:app --reload   (from 09-fastapi-pro-di-auth-config/)
Swagger UI:   http://127.0.0.1:8000/docs  (click "Authorize", log in via /auth/token)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from secureapp.auth_router import router as auth_router
from secureapp.dependencies import get_settings
from secureapp.errors import register_exception_handlers
from secureapp.middleware import register_middleware
from secureapp.tasks_router import router as tasks_router

settings = get_settings()

app = FastAPI(title="Tasks API — module 09 (DI + JWT auth + config)", version="0.9.0")

# CORS ≈ Spring's CorsConfigurationSource. Browsers enforce it, curl doesn't.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_middleware(app)  # ≈ registering a servlet Filter
register_exception_handlers(app)  # ≈ @ControllerAdvice

app.include_router(auth_router)
app.include_router(tasks_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
