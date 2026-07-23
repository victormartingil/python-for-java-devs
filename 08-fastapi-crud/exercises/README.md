# 08 — Exercises: FastAPI CRUD

One app, three missing features. The exercise app (`ex08_app.py`) is module 08's tasks API with three holes punched in it — each in a different file, like real feature work.

```bash
uv run pytest 08-fastapi-crud/exercises -v
```

| Exercise | File | Goal |
|---|---|---|
| 01 | `ex08_router.py` | Add `GET /tasks/stats` returning `TaskStats` — mind route order vs `/{task_id}` |
| 02 | `ex08_schemas.py` | Validate `TaskCreate.title`: strip whitespace, reject blank (422) |
| 03 | `ex08_store.py` | Implement `TaskStore.search` — case-insensitive substring on title |

Implement in any order — each test file targets one feature.

**Don't read `solutions/` until your tests pass — the tests are the spec.** Solutions are reference implementations, not the only correct answer.
