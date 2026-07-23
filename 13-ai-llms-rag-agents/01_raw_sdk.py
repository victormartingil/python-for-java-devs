"""01 — The raw SDK: no framework, just an HTTP client with opinions.

Before any framework: what an LLM call actually IS. A POST with a list of
messages ({role: system|user|assistant, content}) and sampling parameters.
Everything LangChain does later is convenience on top of this exact shape.

Java anchor: think of this as calling the API with a bare RestClient — you'd
never build an app that way, but you must know what the framework hides.

Shows: system/user messages · temperature · STRUCTURED OUTPUT — the model
returns JSON that we validate against a Pydantic schema (≈ mapping the
response body onto a record with Jackson + Bean Validation).

Run:  uv run python 13-ai-llms-rag-agents/01_raw_sdk.py
No API key and no Ollama? The script prints setup instructions and exits 0.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # scripts run from anywhere

from provider import DEFAULT_CHAT_MODELS, get_provider, provider_status
from pydantic import BaseModel, Field


class TicketClassification(BaseModel):
    """The contract the model must satisfy (≈ the response DTO)."""

    category: str = Field(description="one of: billing, technical, account, other")
    priority: str = Field(description="one of: low, medium, high")
    summary: str = Field(description="one sentence, max 20 words")


SYSTEM_PROMPT = (
    "You are a strict JSON API. Classify the user's support ticket. "
    "Answer with ONLY a JSON object matching this JSON Schema — no prose, no markdown fences:\n"
    + json.dumps(TicketClassification.model_json_schema())
)

TICKET = "My invoice shows a charge after I cancelled my subscription last month."


def classify_with_openai() -> TicketClassification:
    from openai import OpenAI

    client = OpenAI()  # reads OPENAI_API_KEY
    response = client.chat.completions.create(
        model=DEFAULT_CHAT_MODELS["openai"],
        temperature=0,  # 0 = deterministic-ish; >1 = creative. ≈ a sampling knob, not a seed.
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": TICKET},
        ],
        response_format={"type": "json_object"},  # native JSON mode
    )
    content = response.choices[0].message.content or "{}"
    # Pydantic validates what the model claims: bad JSON or wrong shape → ValidationError.
    return TicketClassification.model_validate_json(content)


def classify_with_anthropic() -> TicketClassification:
    import anthropic

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    message = client.messages.create(
        model=DEFAULT_CHAT_MODELS["anthropic"],
        max_tokens=300,
        temperature=0,
        system=SYSTEM_PROMPT,  # Anthropic: system is a top-level param, not a message
        messages=[{"role": "user", "content": TICKET}],
    )
    text = "".join(block.text for block in message.content if block.type == "text")
    return TicketClassification.model_validate_json(text)


def classify_with_ollama() -> TicketClassification:
    # Ollama speaks the OpenAI wire format at localhost:11434/v1 — same client, other base_url.
    from openai import OpenAI

    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    response = client.chat.completions.create(
        model=DEFAULT_CHAT_MODELS["ollama"],
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": TICKET},
        ],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    return TicketClassification.model_validate_json(content)


def main() -> None:
    provider = get_provider()
    ok, instructions = provider_status(provider)
    if not ok:
        print(f"Cannot run the demo with LLM_PROVIDER={provider!r}.\n\n{instructions}")
        return

    classify = {
        "openai": classify_with_openai,
        "anthropic": classify_with_anthropic,
        "ollama": classify_with_ollama,
    }[provider]

    print(f"Provider: {provider} · model: {DEFAULT_CHAT_MODELS[provider]}")
    print(f"Ticket:   {TICKET}\n")
    result = classify()
    print("Validated structured output (Pydantic):")
    print(f"  category: {result.category}")
    print(f"  priority: {result.priority}")
    print(f"  summary:  {result.summary}")


if __name__ == "__main__":
    main()
