"""02 — LangChain LCEL: prompt | model | parser.

LCEL (LangChain Expression Language) composes Runnables with the pipe
operator — a fluent builder, closer to Java Streams than to Spring:
each stage takes the previous stage's output.

    ChatPromptTemplate  →  renders {variables} into messages
    | chat model        →  messages in, AIMessage out
    | output parser     →  AIMessage in, str (or a validated object) out

When is a chain enough? Classification, extraction, summarization,
translation — one LLM call, linear flow, no decisions, no loops. The moment
you need the model to DECIDE something (call a tool? retrieve? loop?), you
want a graph — that's script 04.

Run:  uv run python 13-ai-llms-rag-agents/02_langchain_lcel.py
"""

import sys
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).resolve().parent))

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from provider import get_chat_model, get_provider, provider_status
from pydantic import BaseModel, Field

REVIEW = (
    "The migration tool worked eventually, but the error messages were cryptic "
    "and I lost two hours on a typo in the config path. Would still recommend."
)


class ReviewAnalysis(BaseModel):
    sentiment: str = Field(description="one of: positive, negative, mixed")
    main_complaint: str | None = Field(description="the single biggest issue, if any")
    would_recommend: bool


def plain_chain_demo() -> None:
    """prompt | model | StrOutputParser — the 'hello world' of LCEL."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Summarize the user's text in exactly {word_count} words. No preamble."),
            ("user", "{text}"),
        ]
    )
    chain = prompt | get_chat_model() | StrOutputParser()
    # .invoke() runs the whole pipeline; .stream() / .batch() / .ainvoke() come free.
    summary = chain.invoke({"word_count": 12, "text": REVIEW})
    print(f"Summary (12 words): {summary}\n")


def structured_chain_demo() -> None:
    """with_structured_output: tool-call/JSON-mode under the hood, Pydantic on top —
    the same contract as script 01, without hand-rolled parsing."""
    model = get_chat_model()
    structured = model.with_structured_output(ReviewAnalysis)
    prompt = ChatPromptTemplate.from_messages(
        [("system", "Analyze the product review."), ("user", "{text}")]
    )
    chain = prompt | structured
    # with_structured_output's static type is dict | BaseModel; at runtime the
    # parsed Pydantic model comes back — cast documents that contract for mypy.
    analysis = cast(ReviewAnalysis, chain.invoke({"text": REVIEW}))
    print("Structured output (validated):")
    print(f"  sentiment:       {analysis.sentiment}")
    print(f"  main_complaint:  {analysis.main_complaint}")
    print(f"  would_recommend: {analysis.would_recommend}")


def main() -> None:
    provider = get_provider()
    ok, instructions = provider_status(provider)
    if not ok:
        print(f"Cannot run the demo with LLM_PROVIDER={provider!r}.\n\n{instructions}")
        return

    print(f"Provider: {provider}")
    print(f"Review:   {REVIEW}\n")
    plain_chain_demo()
    structured_chain_demo()


if __name__ == "__main__":
    main()
