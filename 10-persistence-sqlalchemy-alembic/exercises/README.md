# 10 — Exercises: persistence (SQLAlchemy)

Two repository exercises against **real PostgreSQL** — same discipline as the module's own tests. They are marked `postgres` and **skip cleanly when no database is reachable**, so nothing breaks on a machine without one.

```bash
cd 10-persistence-sqlalchemy-alembic && docker compose up -d   # start the DB first
uv run pytest 10-persistence-sqlalchemy-alembic/exercises -v
```

| Exercise | Stub | Goal |
|---|---|---|
| 01 | `ex10_repository.py` | Add `count()` (≈ `countByCompleted`) and `list_page()` (≈ `Pageable`) to module 10's repository |
| 02 | `ex10_search.py` | Add a case-insensitive title search with `ilike` (≈ `findByTitleContainingIgnoreCase`) |

Both extend the module's real `TaskRepository` — you write the queries, not the plumbing.

**Don't read `solutions/` until your tests pass — the tests are the spec.** Solutions are reference implementations, not the only correct answer.
