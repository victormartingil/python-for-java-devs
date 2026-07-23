# 08 — FastAPI CRUD

**Goal:** your first API. The tasks API starts here as an in-memory CRUD and evolves through modules 09 → 11 → 14 into a production service.

## Run it

*Requires: `uv sync --group web`*

```bash
uv sync --group web                          # once, from the repo root
cd 08-fastapi-crud
uv run uvicorn tasks_app:app --reload          # ≈ mvn spring-boot:run (+ DevTools reload)
```

Then open <http://127.0.0.1:8000/docs> — full interactive Swagger UI, generated from your type hints. That is springdoc-openapi, except it costs you **zero** configuration and can never drift out of sync with the code.

## FastAPI ↔ Spring Boot

| Spring Boot | FastAPI | Here |
|---|---|---|
| `@SpringBootApplication` class | `app = FastAPI()` | `tasks_app.py` |
| `@RestController` + `@RequestMapping("/tasks")` | `APIRouter(prefix="/tasks")` | `tasks_router.py` |
| `@PostMapping` / `@GetMapping` / ... | `@router.post(...)` / `@router.get(...)` | `tasks_router.py` |
| `@PathVariable` | `def get_task(task_id: int)` — the `{task_id}` in the path binds by name | `tasks_router.py` |
| `@RequestParam(required = false)` | `completed: bool \| None = None` | `list_tasks` |
| `@RequestBody @Valid` | `data: TaskCreate` — a Pydantic model | `create_task` |
| DTO records + Bean Validation | Pydantic `BaseModel` + `Field(min_length=1)` | `tasks_schemas.py` |
| `@ResponseStatus(CREATED)` | `status_code=status.HTTP_201_CREATED` | `create_task` |
| `ResponseStatusException` | `raise HTTPException(404, ...)` | `get_task` |
| springdoc-openapi | Swagger UI at `/docs`, OpenAPI at `/openapi.json` — built in | — |
| `mvn spring-boot:run` | `uv run uvicorn tasks_app:app --reload` | — |
| MockMvc | `TestClient` (httpx2-based, in-process) | `tests/` |

Two things worth noticing as a Java dev:

1. **Validation is declarative and total.** `task_id: int` means `GET /tasks/abc` never reaches your code — FastAPI answers 422 with a precise error body. Same for the JSON body against `TaskCreate`.
2. **`def` vs `async def`.** Plain `def` endpoints run in a thread pool; `async def` endpoints run on the event loop. Both are fine here (no I/O). The rule for later modules: use `async def` when you `await` async I/O (module 10), never block the loop with sync I/O in an `async def`.

## Why three schemas (Create / Update / Response)

One `Task` class for everything is the Spring tutorial anti-pattern you already know. Here it bites harder because JSON is untyped at the boundary:

- **`TaskCreate` has no `id`.** If it did, a client could send one (mass assignment). The server assigns ids.
- **`TaskUpdate` is all-optional** — PATCH semantics. `model_dump(exclude_unset=True)` tells apart "field not sent" from "field sent as null".
- **`TaskResponse` is the public contract.** Internal fields added later (owner, timestamps) don't leak unless you add them here.
- **`extra="forbid"`** rejects unknown fields with a 422 instead of silently dropping them (`{"title": "x", "admin": true}` should not "work").

## Status codes used

| Code | When | Spring equivalent |
|---|---|---|
| 201 | task created | `@ResponseStatus(CREATED)` |
| 204 | deleted, no body | `@ResponseStatus(NO_CONTENT)` |
| 404 | id not found | `ResponseStatusException` |
| 422 | validation failed | `MethodArgumentNotValidException` (400 in Spring) |

FastAPI uses **422** (not 400) for validation errors — it's in the OpenAPI spec automatically, so clients can rely on it.

## Flask / Django / FastAPI in 10 lines (context, then we move on)

- **Flask**: microframework, sync, you assemble everything yourself (validation, OpenAPI, DI — all third-party). Fine for tiny services; you rebuild Spring's features by hand.
- **Django**: batteries-included monolith — ORM, admin, templates, auth. Aimed at server-rendered sites; DRF adds APIs on top. Heavy if all you want is a JSON API.
- **FastAPI**: API-first, async-native, type-hint-driven (validation + OpenAPI for free). The closest thing to Spring Boot for JSON APIs, and the 2026 default for new Python backends — which is why this repo uses it.

## The tests ≈ MockMvc

```bash
uv run pytest 08-fastapi-crud/tests -v
```

`tests/test_tasks_api.py` uses `TestClient(app)` — real HTTP semantics in-process, no server needed. Notice what's missing vs MockMvc: no builders, no `.andExpect(jsonPath(...))`; you write `response.json()["title"] == "..."` and plain `assert`.

## Common pitfalls for Java devs

- **Returning internal models.** Returning your store/ORM object directly works... until it leaks fields. `response_model=TaskResponse` is the seatbelt — FastAPI serializes through it no matter what you return.
- **Forgetting `status_code=201`.** FastAPI defaults to 200 for everything, including POST.
- **Mutable module-level state.** `store` here is a singleton dict — fine for a demo, wrong for real apps. Module 09 injects dependencies properly, module 10 moves state to PostgreSQL.
- **`uvicorn` vs `uvicorn --reload`.** Reload is for development only; module 14 covers production serving (workers, graceful shutdown).

## Dig deeper

- FastAPI tutorial (excellent, read it like reference docs): <https://fastapi.tiangolo.com/tutorial/>
- Pydantic v2 models: <https://docs.pydantic.dev/latest/concepts/models/>
