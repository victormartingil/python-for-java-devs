# 11 — Project architecture ⭐

**The question this module answers:** *"In Java/Spring the reference is hexagonal architecture. What's the equivalent — equally rigorous — standard in Python?"*

**The honest answer:** the settled best practice in the FastAPI ecosystem is **not** formal ports & adapters. It's a **domain-modular layered architecture** that achieves the same goals — testability, low coupling, the ability to swap infrastructure — with less ceremony, leaning on duck typing and dependency injection. This module is the tasks API from module 10 (plus the auth from module 09) refactored to that standard. This is the structure modules 12–14 build on.

## Run it

*Requires: `uv sync --group web`*

```bash
cd 11-project-architecture
docker compose up -d
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

## The structure

```
app/
├── main.py               # Composition root: create app, register routers
│                         #   (≈ the @SpringBootApplication class)
├── core/                 # Cross-cutting infra, shared by all domains
│   ├── config.py         #   typed settings (≈ application.yml)
│   ├── database.py       #   engine + session factory + Base (≈ DataSource)
│   ├── security.py       #   Argon2 hashing + PyJWT
│   ├── exceptions.py     #   domain errors + global handlers (≈ @ControllerAdvice)
│   └── logging.py        #   logging setup (structlog arrives in module 14)
├── dependencies.py       # DI wiring with Depends (≈ @Configuration + @Bean)
├── tasks/                # A domain module (≈ a bounded context)
│   ├── router.py         #   HTTP layer — thin (≈ @RestController)
│   ├── schemas.py        #   Pydantic DTOs — the ONLY public shape
│   ├── service.py        #   business logic — no FastAPI, no SQLAlchemy
│   ├── repository.py     #   data access — Protocol + Postgres + in-memory
│   └── models.py         #   ORM entities — never leave the repository
└── users/                # Second domain module — same internal structure
    └── (router, schemas, service, repository, models)
```

Dependency direction: `router → service → repository`. `core/` is shared by all domains; domains don't import each other. Scaling = adding domain folders, not more layers.

## The 5 golden rules

1. **Thin routers.** HTTP enters and leaves in `router.py`: parse, call service, return. If a router contains an `if` about business rules, it leaked.
2. **Schemas ≠ ORM models.** `schemas.py` is the API contract; `models.py` is the persistence mapping. Conflating them is how `hashed_password` ends up in a JSON response.
3. **Framework-agnostic services.** `service.py` imports no FastAPI and no SQLAlchemy. It speaks DTOs, domain records and domain exceptions — so it tests with plain pytest, no app, no DB (`tests/test_task_service.py` runs in milliseconds).
4. **DI with `Depends`.** All object construction lives in `dependencies.py`. Swapping Postgres ↔ in-memory touches zero domain code — **the same benefit ports & adapters gives you, with less code**. The tests do it live via `app.dependency_overrides`.
5. **Modules by domain, not by technical type.** `tasks/` and `users/`, not `controllers/` + `services/` + `daos/`. A feature lives in one folder; deleting a feature is deleting one folder.

## Concept mapping: hexagonal → this architecture

| Hexagonal (Java) | Here | How the decoupling actually works |
|---|---|---|
| Port (interface) | `TaskRepository` **Protocol** + `Depends` | structural typing — see below |
| Adapter (JPA impl) | `SqlAlchemyTaskRepository` in `repository.py` | constructed in `dependencies.py` |
| Use case / app service | `TaskService` in `service.py` | depends on the Protocol, not the impl |
| Domain model | `TaskRecord` dataclass + schemas | plain objects, no ORM annotations |
| Composition root | `dependencies.py` + `main.py` | the only place concrete classes are named |
| `@MockBean` in tests | `app.dependency_overrides[...]` | see `tests/conftest.py` |

## Why Python converged here (and Java didn't)

- **Structural vs nominal typing.** Java needs `interface TaskRepository` + `implements` or nothing compiles. Python has `typing.Protocol` (module 04): any object with the right methods *is* a `TaskRepository` — no inheritance, no registration. The "port" costs 6 lines and exists mainly for mypy and readers; the runtime never needed it.
- **Duck typing + DI = the swap for free.** `TaskService(repo)` accepts anything with `async def create/list/get/update/delete`. The Postgres repository and the in-memory test fake share no base class. Formal ports & adapters would buy you nothing extra at runtime.
- **Culture.** "Simple is better than complex" (Zen of Python). The community tried Java-style ceremony (zope.interface, ABC-heavy frameworks) and rejected it; the ecosystem converged on small, explicit, convention-driven structure. FastAPI's own docs and the big open-source FastAPI codebases all look like this module.

## When to harden toward formal hexagonal

Stay here by default. Escalate when you have **multiple real adapters** for the same port (Postgres *and* a REST *and* an event source behind one interface), an **anti-corruption layer** over a legacy/external system, or a team large enough that enforced boundaries beat conventions. The upgrade path is incremental — you already have the pieces:

```python
from typing import Protocol

class TaskRepository(Protocol):          # the port, made explicit (already done here)
    async def get(self, task_id: int) -> TaskRecord | None: ...

# Next steps if you outgrow this module:
# - move Protocols + records to app/<domain>/ports.py, adapters to infrastructure/
# - enforce import direction with a tool (import-linter) instead of convention
# - keep services free of Pydantic too (domain objects in, domain objects out)
```

That's it — no second framework, no parallel class hierarchy. The architecture in this module *is* the first 80% of hexagonal.

## The killer demo: tests per layer

```bash
uv run pytest 11-project-architecture/tests -v
```

- **`test_task_service.py` / `test_user_service.py`** — pure domain tests: service + `InMemoryTaskRepository`, no FastAPI, no DB, no HTTP. ≈ JUnit tests of a `@Service` with a stubbed repo. (pytest-asyncio runs the `async` tests; configured repo-wide.)
- **`test_layered_api.py`** — full HTTP stack: real app, real routers, real services, real JWT auth — but `tests/conftest.py` does this:

```python
app.dependency_overrides[get_task_repository] = lambda: InMemoryTaskRepository()
```

That is `@MockBean`, minus the magic: the container's wiring, replaced for the test's lifetime. Same HTTP contract as module 10's Postgres-backed tests — different adapter, zero code changes. **This is the architecture paying rent.**

Compare the three levels you'll combine in module 12 (the full pyramid): pure service tests (fast, most of them) → API tests with fakes (this module) → repository/integration tests against real Postgres (module 10) → testcontainers (module 12).

## Common pitfalls for Java devs

- **Building a parallel `interfaces/` package.** Unneeded ceremony — a `Protocol` next to the implementations is enough. Let pain, not habit, drive abstraction.
- **Importing FastAPI in services "just for `HTTPException`".** That's the layering breach. Raise domain exceptions; `core/exceptions.py` maps them to HTTP once.
- **Returning ORM models from services.** The repository returns `TaskRecord`; the service returns `TaskResponse`. Two cheap dataclasses stand between your DB and your API.
- **Circular imports between domains.** `tasks/` never imports `users/`. Cross-domain needs go through `core/` or explicit service calls — same rule as bounded contexts.
- **Fat `dependencies.py` anxiety.** It *should* name every concrete class — that's the point of a composition root. It's the only file you're allowed to wire in.

## Dig deeper

- FastAPI: dependencies, larger applications: <https://fastapi.tiangolo.com/tutorial/bigger-applications/>
- `typing.Protocol` (PEP 544) — module 04 of this repo first: <https://peps.python.org/pep-0544/>
- Cosmic Python (the "patterns book" for Python, ports & adapters translated): <https://www.cosmicpython.com/>
