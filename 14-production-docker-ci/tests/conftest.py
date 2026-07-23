"""Test wiring for module 14 — the production app with in-memory repositories.

Same pattern as module 11: the REAL app (prodapp wrapping module 11's app),
with repositories swapped for fakes via app.dependency_overrides. Offline,
fast, no Docker — the Dockerfile/compose verification is a manual step
documented in the README (and was run during development).
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

MODULE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = MODULE_DIR.parent

# prodapp imports `app` (module 11) as a top-level package — both on sys.path.
sys.path.insert(0, str(REPO_ROOT / "11-project-architecture"))
sys.path.insert(0, str(MODULE_DIR))

try:  # gated deps (web group) — the root conftest skips this dir when absent
    from app.dependencies import get_task_repository, get_user_repository  # noqa: E402
    from app.tasks.repository import InMemoryTaskRepository  # noqa: E402
    from app.users.repository import InMemoryUserRepository  # noqa: E402
    from fastapi.testclient import TestClient
    from prodapp.jobs import SENT_WELCOME_EMAILS  # noqa: E402
    from prodapp.main import app  # noqa: E402
except ModuleNotFoundError:  # light `uv sync` profile — tests never run here
    TestClient = None  # type: ignore[assignment]


@pytest.fixture
def client() -> Iterator[TestClient]:
    task_repo = InMemoryTaskRepository()
    user_repo = InMemoryUserRepository()
    app.dependency_overrides[get_task_repository] = lambda: task_repo
    app.dependency_overrides[get_user_repository] = lambda: user_repo
    SENT_WELCOME_EMAILS.clear()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
