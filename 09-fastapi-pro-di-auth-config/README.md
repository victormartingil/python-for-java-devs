# 09 — FastAPI pro: DI, auth & config

**Goal:** turn module 08's demo into something structured: dependency injection, typed configuration, global error handling, middleware, CORS — and **JWT authentication with the current, maintained stack**.

## Run it

*Requires: `uv sync --group web`*

```bash
cd 09-fastapi-pro-di-auth-config
cp .env.example .env        # optional — defaults work for local dev
uv run uvicorn secureapp.main:app --reload
```

Try it in Swagger UI (<http://127.0.0.1:8000/docs>): `POST /auth/register`, then click **Authorize** and log in — Swagger knows the OAuth2 flow because of `OAuth2PasswordBearer`.

## `Depends` ≈ `@Autowired`

FastAPI's DI is one function: `Depends`. A dependency is any callable; FastAPI calls it per request and injects the result. Dependencies can depend on dependencies — the container builds the graph:

```
create_task endpoint
  ├─ TaskStoreDep        → get_task_store()      (the "repository")
  └─ CurrentUserDep      → get_current_user()
       ├─ oauth2_scheme      → extracts "Authorization: Bearer <token>" (401 if absent)
       ├─ SettingsDep        → get_settings()    (lru_cached singleton bean)
       └─ UserStoreDep       → get_user_store()
```

| Spring | FastAPI |
|---|---|
| `@Bean` / `@Component` | a function passed to `Depends(...)` |
| `@Autowired` constructor param | endpoint parameter `store: TaskStoreDep` |
| `@ConfigurationProperties` singleton | `@lru_cache def get_settings()` |
| `@MockBean` in tests | `app.dependency_overrides[...] = ...` (module 11 demos this hard) |

No annotations on classes, no component scan: the wiring is explicit function composition. The `Annotated[Settings, Depends(get_settings)]` aliases in `dependencies.py` are the modern style — the type stays the real type, the wiring rides along.

## Configuration ≈ `application.yml`

`secureapp/config.py`: a `BaseSettings` subclass. Env vars bind case-insensitively (`SECRET_KEY` → `secret_key`); a local `.env` file is read for dev; invalid/missing values fail fast at import with a typed error. `.env.example` documents the knobs; `.env` itself is gitignored (repo-wide rule — check the root `.gitignore`).

## Global exceptions ≈ `@ControllerAdvice`

Module 08 did `try/except → HTTPException` in every endpoint. Module 09 moves that to `errors.py`: `@app.exception_handler(TaskNotFoundError)` registered once — endpoints just raise domain exceptions. Same mental model as `@ExceptionHandler` methods.

## Middleware ≈ servlet filters

`middleware.py` adds an `X-Process-Time-Ms` header to every response — the `call_next(request)` line is your `filterChain.doFilter(...)`. Use middleware for cross-cutting mechanics (timing, logging, correlation ids); use dependencies for auth so it appears in OpenAPI. CORS is `app.add_middleware(CORSMiddleware, ...)` ≈ Spring's `CorsConfigurationSource`.

## JWT auth: the flow

1. `POST /auth/register` — hash the password with **Argon2id** (`pwdlib`), store the user, return `UserResponse` (never the hash).
2. `POST /auth/token` — OAuth2 password grant: form-encoded `username`/`password` → signed JWT with `sub`, `iat`, `exp` (**PyJWT**).
3. Protected endpoints declare `current_user: CurrentUserDep` → `get_current_user` verifies signature + expiry and loads the user, or 401.
4. `jwt.decode(..., algorithms=[settings.algorithm])` — the algorithm is **pinned explicitly**. Decoding without it is the classic algorithm-confusion attack.

> ⚠️ **If a tutorial uses `python-jose` or `passlib`, it's outdated. Walk away.**
>
> - **`python-jose`** is unmaintained and has a known CVE (**CVE-2024-33663**, algorithm-confusion). Most 2021–2023 FastAPI tutorials still use it.
> - **`passlib`** has had no release since 2020 and is **broken with bcrypt ≥ 5** (it crashes reading bcrypt's version). You will hit this.
> - The **official FastAPI docs now use PyJWT + pwdlib with Argon2** — and Argon2id is the OWASP-recommended password-hashing algorithm. That's what this module (and this repo) uses.

## The tests

```bash
uv run pytest 09-fastapi-pro-di-auth-config/tests -v
```

- `test_auth_api.py` — the full flow: register → login → call a protected endpoint → 401 without token → 401 with a **tampered** token → 401 with an **expired** token → 401 with a token signed by the wrong key. Duplicate registration → 409.
- `test_secured_tasks_api.py` — the CRUD from module 08 behind auth; every `/tasks` endpoint returns 401 unauthenticated; 404s now come from the global handler; the middleware header is present.

## Common pitfalls for Java devs

- **Instantiating `Settings()` in every endpoint.** Use the `lru_cache`'d `get_settings` dependency — one instance, and tests can override it.
- **Doing auth in middleware.** It works but stays invisible to OpenAPI and can't 401 selectively per route. `Depends(get_current_user)` is the idiomatic way.
- **Returning the ORM/store record.** `UserRecord` has `hashed_password`; the endpoint returns `UserResponse`. The schema boundary is what protects you.
- **"It worked in the tutorial" dependencies.** Check maintenance status before adding auth libraries — the FastAPI ecosystem moved on (see the warning box).

## Dig deeper

- FastAPI security tutorial (OAuth2 + JWT, the current stack): <https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/>
- pydantic-settings: <https://docs.pydantic.dev/latest/concepts/pydantic_settings/>
- OWASP password storage cheat sheet (why Argon2id): <https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html>
