"""SOLUTION 09-02 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class FeatureSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FEATURE_", extra="ignore")

    beta_dashboard: bool = False
    max_tasks_per_user: int = 50


def capacity_summary(settings: FeatureSettings) -> dict[str, object]:
    return {
        "beta_dashboard": settings.beta_dashboard,
        "max_tasks_per_user": settings.max_tasks_per_user,
    }
