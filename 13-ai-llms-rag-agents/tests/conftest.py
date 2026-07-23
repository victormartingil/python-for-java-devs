"""Test wiring for module 13 — sys.path to the scripts + a hermetic LLM env.

All tests in this directory run OFFLINE: no API keys, no Ollama, no Docker.
monkeypatch controls every env var; subprocess tests strip provider keys.
"""

import sys
from pathlib import Path

import pytest

MODULE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MODULE_DIR))


@pytest.fixture
def clean_llm_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    """No provider configured: ollama 'unreachable', no API keys."""
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("EMBEDDINGS_PROVIDER", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    # Deterministic offline: pretend the Ollama port is closed even if a
    # developer has `ollama serve` running on their machine.
    monkeypatch.setattr("provider._ollama_reachable", lambda: False)
    return monkeypatch
