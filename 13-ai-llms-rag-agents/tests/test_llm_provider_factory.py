"""Provider factory tests — offline, no network, no API keys, no Ollama.

The factory is the seam every script depends on (≈ testing your
@Configuration class with different Spring profiles active): given an env
var combination, does the right client come out, and does the status check
report the right thing? Construction must never touch the network.
"""

import os
import subprocess
import sys
from pathlib import Path

import provider
import pytest
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

MODULE_DIR = Path(__file__).resolve().parent.parent


# --- provider selection ------------------------------------------------------


def test_default_provider_is_ollama(clean_llm_env: pytest.MonkeyPatch) -> None:
    assert provider.get_provider() == "ollama"


def test_provider_from_env(clean_llm_env: pytest.MonkeyPatch) -> None:
    clean_llm_env.setenv("LLM_PROVIDER", "OpenAI")  # case/whitespace tolerant
    assert provider.get_provider() == "openai"


def test_invalid_provider_fails_loudly(clean_llm_env: pytest.MonkeyPatch) -> None:
    clean_llm_env.setenv("LLM_PROVIDER", "gemini")
    with pytest.raises(ValueError, match="LLM_PROVIDER must be one of"):
        provider.get_provider()


# --- status checks (the pre-flight every script runs) -------------------------


def test_status_openai_without_key(clean_llm_env: pytest.MonkeyPatch) -> None:
    ok, instructions = provider.provider_status("openai")
    assert ok is False
    assert "OPENAI_API_KEY" in instructions


def test_status_openai_with_key(clean_llm_env: pytest.MonkeyPatch) -> None:
    clean_llm_env.setenv("OPENAI_API_KEY", "sk-test-fake")
    ok, instructions = provider.provider_status("openai")
    assert ok is True
    assert instructions == ""


def test_status_ollama_down(clean_llm_env: pytest.MonkeyPatch) -> None:
    ok, instructions = provider.provider_status("ollama")
    assert ok is False
    assert "ollama serve" in instructions


def test_ollama_host_env_var_is_honored(monkeypatch: pytest.MonkeyPatch) -> None:
    """The probe and the langchain_ollama client read the same OLLAMA_HOST —
    so tests can point both at a dead port and stay hermetic on machines
    where a real Ollama is running."""
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    assert provider._ollama_host_port() == ("localhost", 11434)  # default
    monkeypatch.setenv("OLLAMA_HOST", "http://127.0.0.1:9")
    assert provider._ollama_host_port() == ("127.0.0.1", 9)
    ok, instructions = provider.provider_status("ollama")
    assert ok is False  # nothing listens on port 9, even with Ollama running
    assert "127.0.0.1:9" in instructions


def test_require_provider_raises_with_instructions(clean_llm_env: pytest.MonkeyPatch) -> None:
    with pytest.raises(provider.ProviderUnavailableError, match="ollama serve"):
        provider.require_provider()


# --- model construction (offline-safe, no network at __init__) ----------------


def test_chat_model_ollama(clean_llm_env: pytest.MonkeyPatch) -> None:
    model = provider.get_chat_model()
    assert isinstance(model, ChatOllama)


def test_ollama_model_env_override(clean_llm_env: pytest.MonkeyPatch) -> None:
    clean_llm_env.setenv("OLLAMA_MODEL", "qwen3.5:9b")
    model = provider.get_chat_model()
    assert isinstance(model, ChatOllama)
    assert model.model == "qwen3.5:9b"
    # The same resolver feeds script 01's raw-SDK calls — one seam for all.
    assert provider.default_chat_model("ollama") == "qwen3.5:9b"
    assert provider.default_chat_model("openai") == provider.DEFAULT_CHAT_MODELS["openai"]


def test_ollama_model_env_does_not_leak_to_paid_providers(
    clean_llm_env: pytest.MonkeyPatch,
) -> None:
    clean_llm_env.setenv("OLLAMA_MODEL", "qwen3.5:9b")
    clean_llm_env.setenv("LLM_PROVIDER", "openai")
    clean_llm_env.setenv("OPENAI_API_KEY", "sk-test-fake")
    model = provider.get_chat_model()
    assert model.model_name == provider.DEFAULT_CHAT_MODELS["openai"]


def test_chat_model_openai(clean_llm_env: pytest.MonkeyPatch) -> None:
    clean_llm_env.setenv("LLM_PROVIDER", "openai")
    clean_llm_env.setenv("OPENAI_API_KEY", "sk-test-fake")
    model = provider.get_chat_model(temperature=0.7)
    assert isinstance(model, ChatOpenAI)
    assert model.model_name == provider.DEFAULT_CHAT_MODELS["openai"]


def test_chat_model_anthropic(clean_llm_env: pytest.MonkeyPatch) -> None:
    clean_llm_env.setenv("LLM_PROVIDER", "anthropic")
    clean_llm_env.setenv("ANTHROPIC_API_KEY", "sk-ant-test-fake")
    assert isinstance(provider.get_chat_model(), ChatAnthropic)


def test_embeddings_default_to_ollama(clean_llm_env: pytest.MonkeyPatch) -> None:
    assert isinstance(provider.get_embeddings(), OllamaEmbeddings)


def test_embeddings_prefer_openai_when_keyed(clean_llm_env: pytest.MonkeyPatch) -> None:
    clean_llm_env.setenv("OPENAI_API_KEY", "sk-test-fake")
    assert isinstance(provider.get_embeddings(), OpenAIEmbeddings)


def test_embeddings_invalid_provider(clean_llm_env: pytest.MonkeyPatch) -> None:
    clean_llm_env.setenv("EMBEDDINGS_PROVIDER", "cohere")
    with pytest.raises(ValueError, match="EMBEDDINGS_PROVIDER"):
        provider.get_embeddings()


# --- the scripts degrade gracefully (the repo's promise) ----------------------

SCRIPTS = ["01_raw_sdk.py", "02_langchain_lcel.py", "03_rag_pgvector.py", "04_langgraph_agent.py"]


@pytest.mark.slow
@pytest.mark.parametrize("script", SCRIPTS)
def test_llm_scripts_print_instructions_instead_of_crashing(script: str) -> None:
    """No keys, no Ollama, no Docker: every script must exit 0 with guidance."""
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "LLM_PROVIDER")
    }
    # Dead port: force the offline path even on machines with Ollama running.
    env["OLLAMA_HOST"] = "http://127.0.0.1:9"
    result = subprocess.run(
        [sys.executable, str(MODULE_DIR / script)],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr
    assert "ollama" in result.stdout.lower()  # default provider's setup instructions


@pytest.mark.slow
def test_mcp_client_server_roundtrip_needs_no_api_key() -> None:
    """Script 05 works fully offline: MCP is plumbing, not AI."""
    env = {k: v for k, v in os.environ.items() if not k.endswith("_API_KEY")}
    env["OLLAMA_HOST"] = "http://127.0.0.1:9"  # dead port — deterministic offline
    result = subprocess.run(
        [sys.executable, str(MODULE_DIR / "05_mcp_tools.py")],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr
    assert "count_words" in result.stdout
    assert "lookup_course_fact('uv')" in result.stdout
