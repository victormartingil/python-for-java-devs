# 14 — Production: Docker & CI

**The question this module answers:** *"How does the module 11 app become a deployable artifact — image, database, migrations, logs, health checks — and what's the Python-specific stuff I'd get wrong?"*

Module 11's `app/` is reused **unmodified**. The `prodapp/` package wraps it with production concerns; the `Dockerfile` + `docker-compose.yml` package the whole thing.

## Run it

*Requires: `uv sync --group web`*

```bash
cd 14-production-docker-ci
docker compose up --build        # builds the image, starts db + app, runs migrations
curl localhost:8000/health       # → {"status":"ok"}
docker compose logs app          # one JSON object per line
docker compose down -v           # stop and delete the data volume
```

## The Dockerfile, stage by stage

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder   # official Astral image
COPY pyproject.toml uv.lock ./                                  # manifests ONLY
RUN uv sync --frozen --no-dev                                   # cached until deps change

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim              # clean runtime stage
COPY --from=builder /build/.venv /app/.venv                     # just the venv over
COPY 11-project-architecture/... 14-production-docker-ci/prodapp ...
USER appuser                                                    # never run as root
HEALTHCHECK CMD python -c "...urllib... /health"                # ≈ k8s livenessProbe
CMD ["gunicorn", "prodapp.main:app", "-k", "uvicorn.workers.UvicornWorker", ...]
```

Why this shape (each decision has a Java parallel):

- **Multi-stage.** The build stage has uv's cache and resolver; the runtime stage has a venv and your code — nothing else. ≈ building with a JDK image and shipping a JRE image. Final image stays small and carries no build tooling.
- **Manifests before code.** `uv sync` on just `pyproject.toml` + `uv.lock` is cached until dependencies change; editing Python files never re-downloads packages. ≈ the `mvn dependency:go-offline` layer trick. `--frozen` = the lockfile is law, same as CI.
- **`--no-dev`.** pytest/ruff/mypy don't ship. The lockfile covers everything; the *selection* is per-environment.
- **Official `ghcr.io/astral-sh/uv` base.** Python + uv preinstalled, pinned by tag. Alternative pattern if your base is fixed: `pip install uv` in a plain `python:3.12-slim`.
- **`PYTHONPATH` names both module dirs.** The image contains module 11's `app` package and module 14's `prodapp` side by side — the same sys.path trick the tests use, made explicit.

## The compose file, tour

- **`db`** — postgres:16, healthcheck via `pg_isready`, **no host port published**: only the app reaches it, over the internal compose network (`DATABASE_URL` points at the hostname `db` — compose DNS).
- **`app.depends_on: service_healthy`** — migrations never run against a half-started Postgres.
- **`command: sh -c "alembic upgrade head && exec gunicorn ..."`** — the Flyway-on-startup pattern: schema is at `head` before the server accepts traffic. `working_dir` puts us where `alembic.ini` lives. `exec` makes gunicorn replace the shell so signals reach it.
- **Secrets via env** — `SECRET_KEY` comes from the environment (dev default with a loud comment for the demo; a real deployment injects it from your secret store). Nothing secret is baked into the image.

## Observability: structlog + /health

- **structlog** (`prodapp/logging_config.py`) ≈ SLF4J + Logback with a JSON encoder: loggers are grabbed per module, key=value context replaces string concatenation, and *one* config at the composition root renders everything — including uvicorn's and SQLAlchemy's stdlib records — as one JSON object per line. `structlog.contextvars` ≈ MDC. `docker compose logs app | jq` is the demo.
- **`/health`** ≈ Actuator liveness: comes from module 11's app, polled by the Docker `HEALTHCHECK`. A real deployment adds `/health/ready` checking the DB pool (readiness ≠ liveness).

## Background tasks → real queues

`prodapp/jobs.py` demos FastAPI's `BackgroundTasks` (≈ fire-and-forget `@Async`): the response returns 202, the work runs after, in-process. **When you need retries, crash survival, rate limiting, or other-machine workers, that's a real queue — Dramatiq or Celery + Redis/RabbitMQ (≈ JMS).** The endpoint shape doesn't change; `background_tasks.add_task(fn, ...)` becomes `queue.send(...)`. Reach for the queue the day "the email must not get lost" appears in a requirement.

## Deployment notes

- **Workers: 2×CPU+1** — the classic gunicorn formula for I/O-bound ASGI apps (each uvicorn worker is one event loop). The demo runs 2; measure and adjust.
- **Behind a proxy.** gunicorn binds the internal network; nginx/Traefik/ALB terminates TLS, sets `X-Forwarded-*`, and is where rate limiting lives. Uvicorn honors `--proxy-headers` (add it behind a real proxy).
- **Graceful shutdown.** `docker stop` sends SIGTERM → gunicorn stops accepting, lets in-flight requests finish up to `--graceful-timeout 30`, then exits; `stop_grace_period: 40s` gives it room before SIGKILL. In-flight DB transactions roll back; that's why the session-per-request pattern (module 11) matters.
- **No `--reload`, ever, in an image.** Reload is a dev feature; in prod it doubles memory and hides import errors until traffic hits.

## Production checklist

| ✅ | Item | Where it's shown |
|---|---|---|
| ☐ | Lockfile built with `--frozen`, dev deps excluded | `Dockerfile` stage 1 |
| ☐ | Secrets from env/secret store, never in the image or git | compose `environment` |
| ☐ | Non-root user in the container | `Dockerfile` `USER appuser` |
| ☐ | Migrations before traffic | compose `command` |
| ☐ | Health endpoint + orchestrator healthcheck | `/health` + `HEALTHCHECK` |
| ☐ | Structured JSON logs to stdout (no log files in containers) | `logging_config.py` |
| ☐ | Graceful shutdown timeouts aligned (app < orchestrator) | `--graceful-timeout` vs `stop_grace_period` |
| ☐ | CI runs lint + types + tests on every PR | `.github/workflows/ci.yml` (repo root) |

## The CI story

The repo's `.github/workflows/ci.yml` is the pipeline: `ruff check`, `ruff format --check`, `mypy`, `pytest` on every push and PR (≈ a Maven `verify` in GitHub Actions). Tests needing a live database skip without one; the `docker`-marked testcontainers tests **run** — `ubuntu-latest` ships a Docker daemon, same as your Spring CI.

## Common pitfalls for Java devs

- **Baking config into the image.** A jar with `application-prod.yml` inside is already a smell; in Docker it's fatal — images are shared across environments. Env vars or mounted secrets only.
- **One fat process.** "Just `uvicorn`" in prod means no worker management, no graceful restarts. gunicorn+uvicorn-workers is the boring, correct answer (like running the JVM under a process supervisor).
- **Log files inside the container.** stdout JSON or nothing — the orchestrator collects. A container writing `/var/log/app.log` is a disk-full incident practicing.
- **`latest` tags.** Pin base images and let the lockfile pin Python deps; "it worked on my laptop" is a supply-chain choice.
- **Running migrations from your laptop against prod.** Migrations run in the cluster, at startup, before traffic — or in a dedicated CI step. Never ad hoc.

## Dig deeper

- uv in Docker (official guide): <https://docs.astral.sh/uv/guides/integration/docker/>
- structlog: <https://www.structlog.org/>
- gunicorn + uvicorn workers: <https://www.uvicorn.org/deployment/>
- Dramatiq (the Celery you'd pick today): <https://dramatiq.io/>
