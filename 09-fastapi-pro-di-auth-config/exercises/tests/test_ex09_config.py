"""Spec for ex02 (FeatureSettings) — make these pass."""

import pytest
from ex09_config import FeatureSettings, capacity_summary


def test_summary_reports_defaults() -> None:
    assert capacity_summary(FeatureSettings()) == {
        "beta_dashboard": False,
        "max_tasks_per_user": 50,
    }


def test_summary_reports_constructor_overrides() -> None:
    summary = capacity_summary(FeatureSettings(beta_dashboard=True, max_tasks_per_user=7))
    assert summary == {"beta_dashboard": True, "max_tasks_per_user": 7}


def test_env_var_overrides_the_default(monkeypatch: pytest.MonkeyPatch) -> None:
    # ≈ Spring relaxed binding: FEATURE_MAX_TASKS_PER_USER=5 beats the default.
    monkeypatch.setenv("FEATURE_MAX_TASKS_PER_USER", "5")
    assert FeatureSettings().max_tasks_per_user == 5
