"""04 — LangGraph: an agent is a state machine, not a while loop.

The mental shift from chains (script 02): a chain is a fixed pipeline; an
AGENT loops — model decides → maybe call a tool → feed result back → model
decides again — until the model answers. LangGraph makes that loop an
explicit graph you can inspect, persist and interrupt:

    state   MessagesState — the conversation so far (the ONLY thing nodes share)
    nodes   functions: state in, partial state out (agent, tools, human_gate)
    edges   static (agent → human_gate) and CONDITIONAL (tools_condition:
            tool calls? → tools : done) — the routing is data, not if/else in code

Plus the three production features that make LangGraph the 2026 default:
    tool calling        — the model emits structured calls, ToolNode executes them
    durable execution   — a checkpointer persists state per thread (Postgres here)
    human-in-the-loop   — interrupt() pauses the graph mid-run for approval (~10 lines)

Java anchor: a persisted workflow engine (think Camunda/Temporal) where the
"process definition" is code and the LLM is one of the activities.

Run:  uv run python 13-ai-llms-rag-agents/04_langgraph_agent.py
"""

import math
import os
import socket
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent))

from langchain_core.embeddings import Embeddings
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool, tool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt
from provider import get_chat_model, get_embeddings, provider_status

# Sync URL (psycopg) for the checkpointer — same container as script 03.
CHECKPOINT_DATABASE_URL = os.environ.get(
    "CHECKPOINT_DATABASE_URL", "postgresql://tasks:tasks@localhost:5433/rag"
)

# Tiny knowledge base — the agent retrieves from THIS, not from the model's memory.
DOCS = [
    "uv replaces pip and venv in this stack; dependencies are locked in uv.lock.",
    "FastAPI dependency injection uses Depends; tests swap beans via dependency_overrides.",
    "Alembic is the Flyway equivalent: autogenerate migrations from SQLAlchemy models.",
    "The production Dockerfile is multi-stage and uses the official Astral uv image.",
]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def make_tools(embeddings: Embeddings, vectors: list[list[float]]) -> list[BaseTool]:
    """Tools close over their data — built in main(), not at import time."""

    @tool
    def search_docs(query: str) -> str:
        """Search the course knowledge base. Use for ANY question about the stack."""
        query_vector = embeddings.embed_query(query)
        ranked = sorted(
            zip(DOCS, vectors, strict=True),
            key=lambda pair: cosine_similarity(query_vector, pair[1]),
            reverse=True,
        )
        facts = "\n".join(f"{i}. {doc}" for i, (doc, _) in enumerate(ranked[:2], start=1))
        # Small local models follow instructions in the TOOL RESULT better than
        # in the system prompt — so the authority statement travels with the data.
        return f"AUTHORITATIVE FACTS (quote these, ignore your prior knowledge):\n{facts}"

    @tool
    def add_numbers(a: float, b: float) -> float:
        """Add two numbers. Use for arithmetic instead of mental math."""
        return a + b

    @tool
    def send_summary_email(to: str, subject: str, body: str) -> str:
        """Send an email with a summary. SENSITIVE: the graph pauses for human
        approval before this runs (see human_gate)."""
        print(f"  [email SENT] to={to} subject={subject!r} body={body[:80]!r}...")
        return f"email sent to {to}"

    return [search_docs, add_numbers, send_summary_email]


def db_reachable(url: str) -> bool:
    parsed = urlparse(url)
    try:
        with socket.create_connection((parsed.hostname or "localhost", parsed.port or 5432), 0.5):
            return True
    except OSError:
        return False


@contextmanager
def make_checkpointer() -> Iterator[tuple[BaseCheckpointSaver[str], str]]:
    """Postgres when reachable (durable: survives process restarts), in-memory
    otherwise. Same graph either way — persistence is an edge concern."""
    if db_reachable(CHECKPOINT_DATABASE_URL):
        try:
            from langgraph.checkpoint.postgres import PostgresSaver

            with PostgresSaver.from_conn_string(CHECKPOINT_DATABASE_URL) as saver:
                saver.setup()  # creates its tables — idempotent
                yield saver, "postgres"
                return
        except Exception as exc:  # driver/libpq issues → degrade, don't crash
            print(f"(Postgres checkpointer unavailable: {exc} — using in-memory)")
    yield InMemorySaver(), "in-memory"


def build_agent(
    tools: list[BaseTool], checkpointer: BaseCheckpointSaver[str]
) -> CompiledStateGraph:
    model = get_chat_model().bind_tools(tools)

    def agent(state: MessagesState) -> dict[str, list[BaseMessage]]:
        return {"messages": [model.invoke(state["messages"])]}

    def human_gate(state: MessagesState) -> None:
        """Human-in-the-loop in ~10 lines: pause BEFORE sensitive tools run."""
        last = state["messages"][-1]
        sensitive = [
            c for c in getattr(last, "tool_calls", []) if c["name"] == "send_summary_email"
        ]
        if sensitive:
            # Freezes the graph; state is persisted by the checkpointer.
            # On resume, interrupt() returns the value passed to Command(resume=...).
            decision = interrupt({"approve_tool_call": sensitive[0]})
            print(f"  [human] resumed with: {decision!r}")

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent)
    graph.add_node("tools", ToolNode(tools))
    graph.add_node("human_gate", human_gate)
    graph.add_edge(START, "agent")
    graph.add_edge("agent", "human_gate")
    graph.add_conditional_edges("human_gate", tools_condition)  # tool calls? → tools : END
    graph.add_edge("tools", "agent")  # the agentic loop: results go back to the model
    return graph.compile(checkpointer=checkpointer)


def main() -> None:
    ok, instructions = provider_status()
    if not ok:
        print(f"LLM provider not ready.\n\n{instructions}")
        return

    embeddings = get_embeddings()
    vectors = embeddings.embed_documents(DOCS)
    tools = make_tools(embeddings, vectors)

    with make_checkpointer() as (checkpointer, backend):
        durability = "survives restarts" if backend == "postgres" else "is per-process"
        print(f"Checkpointer: {backend} (thread state {durability})")
        agent = build_agent(tools, checkpointer)

        # thread_id = the conversation's primary key in the checkpoint store.
        # A fresh id per run keeps the demo deterministic; reusing an id
        # resumes that thread's persisted state — that IS durable execution.
        config: RunnableConfig = {"configurable": {"thread_id": f"demo-{uuid4().hex[:8]}"}}
        system = (
            "system",
            "You answer questions about the course stack. For ANY stack question, "
            "call search_docs and base your answer ONLY on its results — never on "
            "your own knowledge of other ecosystems. Call ONE tool at a time.",
        )

        # TURN 1 — agentic RAG: the model DECIDES to retrieve before answering.
        question = "What does this stack use instead of pip?"
        print(f"\nQ1: {question}\n")
        result = agent.invoke({"messages": [system, ("user", question)]}, config=config)
        print(f"A1: {result['messages'][-1].content}\n")

        # TURN 2 — same thread: the checkpoint carries turn 1's context, so the
        # email summarizes the GROUNDED answer, not the model's prior knowledge.
        followup = "Email a one-line summary of your answer to team@example.com."
        print(f"Q2: {followup}\n")
        result = agent.invoke({"messages": [("user", followup)]}, config=config)

        # The graph paused at human_gate (send_summary_email is sensitive).
        pending = result.get("__interrupt__", [])
        if pending:
            print(f"  [graph PAUSED — awaiting approval] {pending[0].value}")
            print("  [human] approving...\n")
            resume: Command[str] = Command(resume="yes")
            result = agent.invoke(resume, config=config)

        print(f"A2: {result['messages'][-1].content}")

        # Agentic RAG visible: the model CHOSE when to retrieve and when to send —
        # nothing in the code told it which tools to use or when.
        used = [c["name"] for m in result["messages"] for c in getattr(m, "tool_calls", [])]
        print(f"\nTools the agent decided to call across both turns: {used}")


if __name__ == "__main__":
    main()
