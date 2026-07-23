# Multi-stage build ≈ a Maven "dependencies first, then code" layered jar.
# Build from the REPO ROOT (the app code lives in module 11):
#   docker build -f 14-production-docker-ci/Dockerfile -t tasks-api .
# (docker-compose.yml in this directory does exactly that for you.)

# ---- Stage 1: resolve and install dependencies with uv ----------------------
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
# Build the venv at its FINAL path (/app/.venv): console-script shebangs are
# absolute (#!/app/.venv/bin/python), so a venv built at /build would break
# when copied — uv venvs are not relocatable across paths.
WORKDIR /app

# Copy ONLY the dependency manifests first. This layer is cached until
# pyproject.toml/uv.lock change — code edits never re-download packages
# (≈ mvn dependency:go-offline in a cache-friendly CI job).
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --group web --no-install-project --no-editable \
    && uv pip list > /dev/null  # fail loudly if the venv is inconsistent

# ---- Stage 2: the runtime image ---------------------------------------------
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
# The official Astral image ships Python 3.12 + uv; we need neither Maven nor
# a JDK-style "build vs runtime" split — just the venv from stage 1.

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    # prodapp imports `app` (module 11) and `prodapp` (module 14) as top-level packages.
    PYTHONPATH="/app/11-project-architecture:/app/14-production-docker-ci"

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY 11-project-architecture/app /app/11-project-architecture/app
COPY 11-project-architecture/alembic /app/11-project-architecture/alembic
COPY 11-project-architecture/alembic.ini /app/11-project-architecture/alembic.ini
COPY 14-production-docker-ci/prodapp /app/14-production-docker-ci/prodapp

# Don't run as root — the same reason your Java containers shouldn't.
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# Docker's own liveness probe ≈ a Kubernetes livenessProbe hitting Actuator.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=2)" || exit 1

# gunicorn (process manager ≈ the JVM's container awareness, done right) with
# uvicorn workers (the actual ASGI runtime). NO --reload in production.
# Workers: 2×CPU+1 is the classic starting formula — compose runs 2 for the demo.
# Migrations run BEFORE the server accepts traffic — see docker-compose.yml command.
CMD ["gunicorn", "prodapp.main:app", \
     "-k", "uvicorn_worker.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--graceful-timeout", "30"]
