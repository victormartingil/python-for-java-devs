# 09 — Exercises: FastAPI pro — DI, auth, config

Three focused exercises on module 09's machinery. The exercise tests build a small app from the module's real `secureapp` package plus your exercise files.

```bash
uv run pytest 09-fastapi-pro-di-auth-config/exercises -v
```

| Exercise | Stub | Goal |
|---|---|---|
| 01 | `ex09_router.py` | Protect a `GET /me` endpoint with `CurrentUserDep` (≈ `AuthenticationPrincipal`) |
| 02 | `ex09_config.py` | Add a settings field + use it; env-var override (≈ relaxed binding) |
| 03 | `ex09_errors.py` | Register a global exception handler: `RateLimitError` → 429 (≈ `@ControllerAdvice`) |

**Don't read `solutions/` until your tests pass — the tests are the spec.** Solutions are reference implementations, not the only correct answer.
