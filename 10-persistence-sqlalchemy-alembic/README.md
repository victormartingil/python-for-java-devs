# 10 — Persistence: SQLAlchemy + Alembic

**Goal:** the tasks API, persisted for real. PostgreSQL in Docker, SQLAlchemy 2.0 **async** as the ORM, Alembic for migrations — the Spring Data JPA + Flyway stack, translated.

## Run it

*Requires: `uv sync --group web`*

```bash
cd 10-persistence-sqlalchemy-alembic
docker compose up -d                 # PostgreSQL 16 (user/db/password: tasks)
uv run alembic upgrade head          # ≈ flyway migrate
uv run uvicorn persistapp.main:app --reload
```

## The mapping

| Spring Data JPA | SQLAlchemy 2.0 (async) | Here |
|---|---|---|
| `DataSource` / HikariCP | `create_async_engine(url)` — the pool | `database.py` |
| `EntityManager` / persistence context | `AsyncSession` | `database.py` |
| `@Entity` + `@Id @GeneratedValue` | `class TaskModel(Base): id: Mapped[int] = mapped_column(primary_key=True)` | `models.py` |
| `em.persist()` / `em.find()` / `em.remove()` | `session.add()` / `session.get()` / `session.delete()` | `repository.py` |
| JPQL / derived queries | `select(TaskModel).where(...)` — typed, composable | `repository.py` |
| `OpenEntityManagerInView` (session per request) | `get_session` dependency (`Depends`) | `database.py` |
| `@Transactional` (commit/rollback at boundary) | commit after `yield`, rollback on exception | `database.py` |
| Flyway / Liquibase | **Alembic** | `alembic/` |

Two mindset notes:

1. **Everything is `await`ed.** `asyncpg` speaks to Postgres asynchronously on the event loop — this is the WebFlux model, not the JDBC-blocking one. Endpoints are `async def`; repository methods are `async def`; you `await session.execute(...)`. Never mix in a sync driver (psycopg2) inside `async def` — that's blocking the loop (module 06).
2. **The mapping is the class.** `Mapped[str]` → `NOT NULL`, `Mapped[str | None]` → nullable. mypy reads the same annotations you do; Alembic reads them to autogenerate DDL.

## ORM vs Core ≈ JPA vs JdbcTemplate

SQLAlchemy is two libraries sharing one core:

```python
# ORM (this module): objects, identity map, dirty checking  ≈ JPA/Hibernate
task = await session.get(TaskModel, 1)
task.completed = True                       # UPDATE generated on flush

# Core: SQL expression builder, no objects, you get rows     ≈ JdbcTemplate
from sqlalchemy import update
await session.execute(update(TaskModel).where(TaskModel.id == 1).values(completed=True))
```

Same engine, same session. Default to ORM for domain CRUD; drop to Core for bulk updates/reporting where the identity map is overhead.

*SQLModel in 2 lines:* a wrapper merging Pydantic + SQLAlchemy into one class (nice for small projects, by FastAPI's author). This repo uses SQLAlchemy proper — it's what serious codebases standardize on, and it makes the ORM/DTO boundary explicit.

## Alembic ≈ Flyway

| Flyway | Alembic |
|---|---|
| `V1__create_tasks.sql` | `alembic/versions/0001_create_tasks.py` (Python, has `upgrade()` + `downgrade()`) |
| `flyway migrate` | `uv run alembic upgrade head` |
| `flyway undo` (Teams) | `uv run alembic downgrade -1` — built in |
| schema history table | `alembic_version` table |
| you write SQL by hand | `alembic revision --autogenerate -m "..."` **diffs your models against the DB and writes the migration** — then you review it |

The workflow: change `models.py` → `uv run alembic revision --autogenerate -m "add priority"` → review the generated file → `uv run alembic upgrade head`. `alembic/env.py` is wired to the app's `Settings`, so `DATABASE_URL` is the single source of truth (nothing hardcoded in `alembic.ini`).

## The tests ≈ `@DataJpaTest` + integration tests

```bash
uv run pytest 10-persistence-sqlalchemy-alembic/tests            # skips without a DB — green everywhere
docker compose up -d && uv run pytest -m postgres                # run them for real
```

- Tests are marked **`postgres`** (registered in the root `pyproject.toml`). The `conftest.py` probes the DB with a sub-second TCP check and **skips cleanly** when unreachable — CI and fresh clones stay green; override the location with `DATABASE_URL`.
- Fixtures give each test a clean database (schema ensured + `TRUNCATE ... RESTART IDENTITY` → deterministic ids).
- `test_tasks_db_api.py` runs the whole API against Postgres via `httpx2.AsyncClient` + `ASGITransport` (same event loop as asyncpg — `TestClient` would use a different one), with `app.dependency_overrides[get_session]` swapping in the test session. That's your first `@MockBean`-style override — module 11 turns it into the main testing weapon.
- Module 12 upgrades this to **testcontainers** (Postgres started by the tests themselves — exactly like Java).

## Common pitfalls for Java devs

- **Sync driver in async code.** `postgresql://` (psycopg2) instead of `postgresql+asyncpg://` in the URL will block or fail loudly — check the driver in the URL first.
- **Forgetting `await session.flush()`** before reading a generated id. `add()` only schedules the INSERT (≈ `persist()` without flush).
- **Session leaks across requests.** Never create a global session; the `get_session` dependency gives one per request and closes it (≈ `EntityManager` per tx).
- **Editing applied migrations.** Like Flyway: once shipped, migrations are immutable — write a new one.
- **Modeling defaults as DB defaults.** `mapped_column(default=False)` is a *Python-side* default; the DDL has no `DEFAULT`. Usually what you want — just know the difference.

## Dig deeper

- SQLAlchemy 2.0 tutorial (the `select()` style): <https://docs.sqlalchemy.org/en/20/tutorial/>
- Async ORM guide: <https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html>
- Alembic tutorial: <https://alembic.sqlalchemy.org/en/latest/tutorial.html>
