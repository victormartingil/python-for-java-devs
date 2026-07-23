"""Exercise 09-02 — add a settings field and use it.

pydantic-settings maps env vars onto a typed model (≈ application.yml +
@ConfigurationProperties). FeatureSettings has one field; add another and
surface it in capacity_summary. The tests are the spec:

    uv run pytest 09-fastapi-pro-di-auth-config/exercises -v

Hint: see 09-fastapi-pro-di-auth-config/secureapp/config.py. Field names map
to env vars case-insensitively — here with the prefix FEATURE_.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class FeatureSettings(BaseSettings):
    """TODO(ex02): add `max_tasks_per_user: int = 50`.

    With env_prefix="FEATURE_", the env var FEATURE_MAX_TASKS_PER_USER
    overrides the default — a test proves it with monkeypatch.setenv.
    """

    model_config = SettingsConfigDict(env_prefix="FEATURE_", extra="ignore")

    beta_dashboard: bool = False  # the example field, given


def capacity_summary(settings: FeatureSettings) -> dict[str, object]:
    """TODO(ex02): return {"beta_dashboard": ..., "max_tasks_per_user": ...}
    with both values read from the given settings object."""
    raise NotImplementedError("TODO(ex02): read both fields from settings")
