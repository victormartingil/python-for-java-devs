"""secureapp — the tasks API from module 08, grown up.

Adds: DI with Depends, typed settings (.env), global exception handlers,
middleware, CORS, and JWT auth (PyJWT + pwdlib/Argon2).

Run the API:  uv run uvicorn secureapp.main:app --reload   (from 09-fastapi-pro-di-auth-config/)
Swagger UI:   http://127.0.0.1:8000/docs
"""
