# 11 — Exercises: project architecture

The flagship exercise of the repo: add a feature the way you would in the real architecture — as a **vertical slice through every layer**.

```bash
uv run pytest 11-project-architecture/exercises -v
```

| Exercise | Files | Goal |
|---|---|---|
| 01 — flagship | `ex11_schemas.py` → `ex11_repository.py` → `ex11_service.py` → `ex11_router.py` | Add a `priority` field to tasks: schema (with default + validation) → record → service method → router endpoint. Proven by service tests (in-memory) AND API tests via `dependency_overrides`. |
| 02 | `ex11_books.py` | Implement the in-memory adapter behind a `BookRepository` Protocol yourself (a fresh domain, so you write the pattern instead of copying it). |

Exercise 01 is intentionally ~6 lines of code — but the RIGHT 6 lines, one per layer. `ex11_dependencies.py` and `ex11_app.py` are provided (wiring, not exercises); a stand-in `get_current_user` replaces the real JWT dependency so the slice stays focused.

**Don't read `solutions/` until your tests pass — the tests are the spec.** Solutions are reference implementations, not the only correct answer.
