"""Test wiring for module 12 — imports module 11's app + Docker availability probe.

Two jobs:
1. sys.path: make `11-project-architecture/app` and this module's `notify.py`
   importable (the repo-wide conftest-per-tests-dir convention).
2. `docker` marker: tests using testcontainers need a Docker daemon. When
   none is reachable they SKIP cleanly, like the `postgres` marker in
   module 10 — so `uv run pytest` stays green on any machine (and RUNS in
   CI, where ubuntu-latest has Docker).

Run the Docker-backed tests only:  uv run pytest -m docker
"""

import sys
from pathlib import Path

import pytest

MODULE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = MODULE_DIR.parent

# Order matters: module 11's `app` package first, then this module's files.
sys.path.insert(0, str(REPO_ROOT / "11-project-architecture"))
sys.path.insert(0, str(MODULE_DIR))

# Rancher Desktop / some Docker Desktop setups expose the daemon socket at a
# host-only path (~/.rd/docker.sock) that cannot be bind-mounted into the
# Ryuk reaper container. The VM-internal path /var/run/docker.sock works for
# Docker Desktop, Rancher Desktop, Colima and plain Linux alike — set it as a
# default (any explicit user/CI value wins). Must happen before testcontainers
# is imported, hence here in conftest rather than in the test module.
import os  # noqa: E402

os.environ.setdefault("TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE", "/var/run/docker.sock")


def _docker_available() -> bool:
    """Ping the Docker daemon — the same check @Testcontainers does implicitly."""
    try:
        import docker

        client = docker.from_env(timeout=2)
        client.ping()
        client.close()
        return True
    except Exception:  # daemon down, socket missing, permission denied...
        return False


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if _docker_available():
        return
    skip = pytest.mark.skip(
        reason="Docker daemon not reachable — start Docker Desktop / Rancher Desktop "
        "to run the testcontainers tests (uv run pytest -m docker)"
    )
    for item in items:
        if "docker" in item.keywords:
            item.add_marker(skip)
