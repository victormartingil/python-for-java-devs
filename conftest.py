"""Repo-wide pytest wiring: skip module test dirs whose dependency block is
not installed in the current sync profile (see README's per-block quickstart).

Light profile (`uv sync` — modules 00–07): the web/ai module test dirs are
skipped at collection time instead of failing with ModuleNotFoundError, so a
bare `uv run pytest` stays green on any profile. ≈ a JUnit assumption gating
whole test classes, but decided at collection time.

`collect_ignore` does not cover dirs listed explicitly in `testpaths`
(pytest treats them as command-line args), hence the `pytest_ignore_collect`
hook — it is consulted for every candidate path, initial args included.
"""

import importlib.util
from pathlib import Path

_ROOT = Path(__file__).resolve().parent

# package -> module dirs that need it (a missing package skips its dirs)
_GATED_DIRS = {
    "fastapi": [
        "08-fastapi-crud",
        "09-fastapi-pro-di-auth-config",
        "11-project-architecture",
        "12-advanced-testing",
        "14-production-docker-ci",
    ],
    "sqlalchemy": ["10-persistence-sqlalchemy-alembic"],
    "testcontainers": ["12-advanced-testing"],
    "langchain": ["13-ai-llms-rag-agents"],
}


def _excluded_dirs() -> list[Path]:
    excluded: list[Path] = []
    for package, modules in _GATED_DIRS.items():
        if importlib.util.find_spec(package) is None:
            excluded.extend(_ROOT / module for module in modules)
    return excluded


def pytest_ignore_collect(collection_path: Path) -> bool:
    """Skip gated module dirs when their dependency block isn't installed."""
    return any(collection_path.is_relative_to(excluded) for excluded in _excluded_dirs())
