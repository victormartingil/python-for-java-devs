# python-for-java-devs

[![CI](https://github.com/victormartingil/python-for-java-devs/actions/workflows/ci.yml/badge.svg)](https://github.com/victormartingil/python-for-java-devs/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/deps-uv-blueviolet.svg)](https://docs.astral.sh/uv/)

<p align="center">
  <img
    src="docs/assets/python-for-java-devs-banner.jpg"
    alt="Python for Java developers — skip the basics, learn what changes"
    width="900"
  >
</p>

**Python for senior Java developers — no fluff, no "what is a variable", just the deltas.**

You know Spring Boot, hexagonal architecture, Maven, JPA/Flyway and JUnit. This repo teaches you Python by anchoring every concept to its Java equivalent: *"this is like X, but with these differences."* By the end you can build a deployable, production-minded API with **FastAPI + PostgreSQL + tests + Docker**, and understand the applied AI stack (LangChain / RAG / LangGraph / MCP) — without reading a 500-page book.

## Who this is for

- Senior Java/Spring developers who have **never written Python**.
- People who learn by reading runnable code, not prose.
- Anyone who wants the *idiomatic* Python way, not "Java transcribed into Python".

If you've never used Spring Boot or written tests with JUnit, this repo will move too fast for you.

## What you'll learn

- The modern Python toolchain: **uv**, `pyproject.toml`, ruff, mypy, pytest — mapped to Maven, Checkstyle/Spotless, the compiler, JUnit.
- Python the language, only where it differs from Java: dynamic typing, comprehensions, decorators, `Protocol`, context managers, `asyncio` (and the GIL, honestly explained).
- A real backend stack: **FastAPI, Pydantic, SQLAlchemy 2.0 (async), Alembic, JWT auth (PyJWT + Argon2)** — current, deliberately chosen equivalents of what you use today.
- How a serious Python project is **architected** (the honest answer to "where is my hexagonal architecture?").
- Applied AI with the current stack: official SDKs → LangChain (LCEL) → LangGraph agents + pgvector + MCP.

## Roadmap

| Module | Topic | Java anchor |
|---|---|---|
| [00 — Setup & running](00-setup-and-running/) | Python + uv, running scripts, IDE setup | JDK + Maven install |
| [01 — Python essentials](01-python-essentials/) | Dynamic typing, `None`, f-strings, truthiness, match | `var`, `null`, `Optional`, switch |
| [02 — Collections & comprehensions](02-collections-and-comprehensions/) | list/dict/set/tuple, comprehensions, itertools | Collections + Stream API |
| [03 — Functions & decorators](03-functions-and-decorators/) | First-class functions, `*args/**kwargs`, decorators | Lambdas, AOP / annotations |
| [04 — OOP, classes & protocols](04-oop-classes-and-protocols/) | Classes, dataclasses, `typing.Protocol` | Lombok/records, interfaces |
| [05 — Errors & context managers](05-errors-and-context-managers/) | Exceptions, EAFP, `with` | Checked exceptions, try-with-resources |
| [06 — Async & concurrency](06-async-and-concurrency/) | The GIL, `asyncio`, `gather` | `CompletableFuture`, virtual threads |
| [07 — A real project: uv + pytest + mypy](07-real-project-uv-pytest-mypy/) | `src/` layout, lockfile, linting, typing, testing, debugging | A standard Maven project |
| [08 — FastAPI CRUD](08-fastapi-crud/) | Routers, Pydantic schemas, Swagger UI | `@RestController`, DTOs, springdoc |
| [09 — FastAPI pro: DI, auth, config](09-fastapi-pro-di-auth-config/) | `Depends`, JWT (PyJWT + Argon2), settings | `@Autowired`, Spring Security, `application.yml` |
| [10 — Persistence: SQLAlchemy + Alembic](10-persistence-sqlalchemy-alembic/) | Async ORM, repositories, migrations | Spring Data JPA, Flyway |
| [11 — Project architecture](11-project-architecture/) ⭐ | Layered-by-domain architecture, DI wiring | Hexagonal architecture |
| [12 — Advanced testing](12-advanced-testing/) | Test pyramid, testcontainers, mocks, coverage | JUnit 5 + Mockito + Testcontainers |
| [13 — AI: LLMs, RAG & agents](13-ai-llms-rag-agents/) | SDKs, LangChain, LangGraph, pgvector, MCP | Spring AI |
| [14 — Production: Docker & CI](14-production-docker-ci/) | Multi-stage Dockerfile, compose, observability | Your deployment pipeline |

✏️ Modules **01–06** and **08–11** also have an `exercises/` dir — "make the test pass" practice (see below).

## How to use this repo

```bash
git clone https://github.com/victormartingil/python-for-java-devs.git
cd python-for-java-devs

# Install uv (the only tool you need — it installs Python too):
#   macOS:        brew install uv
#   Linux/macOS:  curl -LsSf https://astral.sh/uv/install.sh | sh
#   Windows:      winget install astral-sh.uv
```

Dependencies are split into blocks (uv groups, ≈ Maven profiles) so you install only what the arc you're reading needs:

```bash
uv sync                  # fundamentals (modules 00–07) — small and fast, ≈ mvn install
uv sync --group web      # + the FastAPI/PostgreSQL arc (modules 08–12, 14)
uv sync --all-groups     # everything: + the AI module (13) and the full quality gates
uv run pytest            # run the test suite for what you installed
```

Module 13 needs both the web and ai blocks (`--group web --group ai`, or just `--all-groups`) — its agent endpoint is FastAPI.

Every example is a runnable script:

```bash
uv run python 01-python-essentials/tour.py
```

Read each module's `README.md` first (5–10 min), then run and read the code. Also grab the [CHEATSHEET.md](CHEATSHEET.md) — the master Java ↔ Python equivalence table.

### Exercises

Reading runnable code gets you to "I recognize this"; writing it gets you to "I can do this". Modules 01–06 and 08–11 ship `exercises/` dirs with JUnit-style practice: TODO stubs + tests that **fail until your implementation is right** (they are NOT part of the root suite — `uv run pytest` stays green). Run a module's set explicitly:

```bash
uv run pytest 01-python-essentials/exercises -v
```

Reference solutions live in `exercises/solutions/` — don't peek until your tests pass; the tests are the spec. Modules 12–14 have no exercises on purpose: those modules already ARE practice-shaped (you build the test pyramid, the AI feature, and the deployment pipeline yourself).

## The golden thread

From module **08 to 14** we build and evolve the same **"tasks" API** — the classic neutral domain:

> in-memory CRUD (08) → DI + JWT auth + config (09) → real PostgreSQL persistence with migrations (10) → production-minded layered architecture (11) → full test pyramid (12) → an AI agent endpoint (13) → Docker + CI deployment (14).

One project, grown the way you'd grow a real service — each module diffs it one step further.

## Ground rules of this repo

- **Zero generic programming theory.** Only deltas vs Java.
- **Runnable by construction.** Examples, tests and exercise solutions are executable; CI enforces lint, types and behavior.
- **Current choices are explicit and checked weekly.** Older tools and patterns (`requirements.txt`, `python-jose`, `passlib`) appear only as labeled context or warnings.
- Stack verified **July 2026**: Python 3.12+, uv, ruff, mypy, pytest, FastAPI, SQLAlchemy 2.0, Alembic, PyJWT + pwdlib (Argon2), LangChain v1 / LangGraph 1.0.

## Repository status

All 15 modules (00–14) complete. Verified end-to-end, July 2026 — the local numbers below assume `uv sync --all-groups`, Docker available and no module 10 PostgreSQL running:

```bash
uv sync --all-groups        # exact dependency versions come from uv.lock
uv run ruff check .         # clean
uv run ruff format --check .# clean
uv run mypy                 # clean, 66 source files
uv run pytest               # 123 passed, 8 skipped
```

The 8 local skips are the `postgres`-marked tests when no database is up (`cd 10-persistence-sqlalchemy-alembic && docker compose up -d` enables them). CI provides PostgreSQL and runs **131 tests with no skips**, verifies every exercise solution, then builds the production image, runs migrations and probes `/health`. The `docker`-marked testcontainers tests (module 12) run automatically when a Docker daemon is available and skip cleanly otherwise. Module 13's AI scripts need an LLM provider — free local [Ollama](https://ollama.com) or an API key; without either they print setup instructions and exit 0 (tests prove it offline). Note: this 2026 stack uses `httpx2` — starlette 1.3.x's `TestClient` and async DB tests are built on it; legacy `httpx` appears only in the early HTTP demos (modules 00, 06).

## Contributing & license

Contributions are welcome (see [CONTRIBUTING.md](CONTRIBUTING.md)). Released under the [MIT License](LICENSE).
