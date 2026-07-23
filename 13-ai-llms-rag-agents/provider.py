"""One factory, three LLM backends ≈ switching a Spring bean with a profile.

Every script in this module gets its model from HERE, so the same code runs
against a paid API or a fully local, free Ollama — no code changes:

    LLM_PROVIDER=ollama      (default — free, local; needs `ollama serve`)
    LLM_PROVIDER=openai      (needs OPENAI_API_KEY)
    LLM_PROVIDER=anthropic   (needs ANTHROPIC_API_KEY)

Embeddings are a separate concern: Anthropic has no embeddings API, so
`get_embeddings()` picks OpenAI when a key is present, otherwise Ollama
(override with EMBEDDINGS_PROVIDER=openai|ollama).

Nothing in this module touches the network at import or construction time:
LangChain clients connect lazily, on first call. `provider_status()` is the
explicit pre-flight check every script runs before doing real work.

Run:  uv run python 13-ai-llms-rag-agents/01_raw_sdk.py
"""

import os
import socket

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel

PROVIDERS = ("ollama", "openai", "anthropic")

# Cheap, current models — agents burn tokens fast, demos don't need flagships.
DEFAULT_CHAT_MODELS = {
    "ollama": "llama3.2",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-haiku-latest",
}
DEFAULT_EMBEDDING_MODELS = {
    "ollama": "nomic-embed-text",
    "openai": "text-embedding-3-small",
}

SETUP_INSTRUCTIONS = {
    "ollama": (
        "Ollama not reachable at localhost:11434.\n"
        "  1. Install:  brew install ollama   (or https://ollama.com)\n"
        "  2. Start:    ollama serve\n"
        "  3. Pull:     ollama pull llama3.2 && ollama pull nomic-embed-text\n"
        "  4. Re-run this script."
    ),
    "openai": (
        "OPENAI_API_KEY is not set.\n"
        "  export OPENAI_API_KEY=sk-...   (or put it in a .env next to the script)\n"
        "  Free alternative: LLM_PROVIDER=ollama (see README)."
    ),
    "anthropic": (
        "ANTHROPIC_API_KEY is not set.\n"
        "  export ANTHROPIC_API_KEY=sk-ant-...\n"
        "  Free alternative: LLM_PROVIDER=ollama (see README)."
    ),
}


class ProviderUnavailableError(RuntimeError):
    """Raised by require_provider() — carries copy-pasteable setup instructions."""


def get_provider() -> str:
    """The active provider from LLM_PROVIDER (default: ollama — free and local)."""
    provider = os.environ.get("LLM_PROVIDER", "ollama").strip().lower()
    if provider not in PROVIDERS:
        raise ValueError(f"LLM_PROVIDER must be one of {PROVIDERS}, got {provider!r}")
    return provider


def _ollama_host_port() -> tuple[str, int]:
    """Where Ollama lives. Honors OLLAMA_HOST — the same env var the
    langchain_ollama client reads, so the probe and the client always agree
    (accepts 'host:port' or a full URL; default localhost:11434)."""
    raw = os.environ.get("OLLAMA_HOST", "").strip() or "localhost:11434"
    raw = raw.removeprefix("http://").removeprefix("https://").rstrip("/")
    host, _, port = raw.partition(":")
    return host or "localhost", int(port) if port.isdigit() else 11434


def _ollama_reachable(host: str | None = None, port: int | None = None) -> bool:
    """Cheap TCP probe — sub-second, no HTTP client needed."""
    if host is None or port is None:
        host, port = _ollama_host_port()
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def provider_status(provider: str | None = None) -> tuple[bool, str]:
    """Pre-flight check: (is_usable, setup_instructions_if_not).

    Scripts call this first and print the instructions instead of crashing —
    like a Spring health indicator for your LLM config.
    """
    provider = provider or get_provider()
    if provider == "ollama":
        ok = _ollama_reachable()
        if ok:
            return True, ""
        host, port = _ollama_host_port()
        return False, SETUP_INSTRUCTIONS["ollama"].replace("localhost:11434", f"{host}:{port}")
    if provider == "openai":
        ok = bool(os.environ.get("OPENAI_API_KEY"))
    else:
        ok = bool(os.environ.get("ANTHROPIC_API_KEY"))
    return ok, "" if ok else SETUP_INSTRUCTIONS[provider]


def require_provider() -> str:
    """Return the provider name or raise with instructions. For scripts that
    would rather fail loudly than print-and-exit."""
    provider = get_provider()
    ok, instructions = provider_status(provider)
    if not ok:
        raise ProviderUnavailableError(instructions)
    return provider


def default_chat_model(provider: str) -> str:
    """The demo model for a provider. For Ollama, OLLAMA_MODEL overrides it —
    local models are pullable artifacts, so make the choice an env var,
    like overriding a Spring property: OLLAMA_MODEL=qwen3.5:9b"""
    if provider == "ollama":
        return os.environ.get("OLLAMA_MODEL", "").strip() or DEFAULT_CHAT_MODELS["ollama"]
    return DEFAULT_CHAT_MODELS[provider]


def get_chat_model(temperature: float = 0.0, model: str | None = None) -> BaseChatModel:
    """A LangChain chat model for the active provider.

    Constructing is offline-safe: the client only connects on first invoke.
    temperature=0 by default — deterministic output makes demos (and tests)
    reproducible; raise it for creative tasks.
    """
    provider = get_provider()
    model = model or default_chat_model(provider)
    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(model=model, temperature=temperature)
    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=model, temperature=temperature)
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(model_name=model, temperature=temperature, timeout=None, stop=None)


def get_embeddings() -> Embeddings:
    """Embeddings for RAG. Anthropic has none → OpenAI if keyed, else Ollama."""
    provider = os.environ.get("EMBEDDINGS_PROVIDER", "").strip().lower()
    if not provider:
        provider = "openai" if os.environ.get("OPENAI_API_KEY") else "ollama"
    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(model=DEFAULT_EMBEDDING_MODELS["openai"])
    if provider == "ollama":
        from langchain_ollama import OllamaEmbeddings

        return OllamaEmbeddings(model=DEFAULT_EMBEDDING_MODELS["ollama"])
    raise ValueError(f"EMBEDDINGS_PROVIDER must be 'openai' or 'ollama', got {provider!r}")
