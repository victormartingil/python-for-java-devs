"""06 — Ship it: the agent as a FastAPI endpoint with SSE streaming.

The payoff of modules 08–11: an agent is just another dependency in a
FastAPI app. This endpoint wraps a small LangGraph agent (model + one
retrieval tool) and streams its progress as Server-Sent Events — the
ChatGPT-style "watch it think" UX, and the pattern behind most production
agent APIs.

    POST /agent/ask {"question": "..."}  → text/event-stream
      data: {"node": "agent", "status": "calling search_docs"}
      data: {"node": "tools", "status": "retrieved 2 docs"}
      data: {"node": "agent", "answer": "..."}
      data: [DONE]

SSE ≈ a one-way WebSocket over plain HTTP: `text/event-stream`, one
`data:` frame per event, connection stays open. Perfect for LLM token/graph
streaming; use WebSockets only when you need bidirectional.

Run:  uv run python 13-ai-llms-rag-agents/06_agent_endpoint.py
Try:  curl -N -X POST localhost:8001/agent/ask \
        -H 'content-type: application/json' \
        -d '{"question": "What replaces pip in this stack?"}'
No provider configured? The endpoint answers 503 with setup instructions —
the app itself always boots.
"""

import json
import math
import sys
from collections.abc import AsyncIterator
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from provider import get_chat_model, get_embeddings, get_provider, provider_status
from pydantic import BaseModel, Field

DOCS = [
    "uv replaces pip and venv; dependencies are locked in uv.lock.",
    "FastAPI uses Depends for DI; tests swap implementations via dependency_overrides.",
    "Alembic is the Flyway equivalent for migrations.",
    "pgvector turns the course Postgres into a vector store with the <=> operator.",
]


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def build_agent() -> CompiledStateGraph:
    """A minimal agentic-RAG graph (the compact cousin of script 04)."""
    embeddings = get_embeddings()
    vectors = embeddings.embed_documents(DOCS)

    @tool
    def search_docs(query: str) -> str:
        """Search the course knowledge base for stack questions."""
        query_vector = embeddings.embed_query(query)
        ranked = sorted(
            zip(DOCS, vectors, strict=True),
            key=lambda pair: cosine_similarity(query_vector, pair[1]),
            reverse=True,
        )
        facts = "\n".join(f"{i}. {doc}" for i, (doc, _) in enumerate(ranked[:2], start=1))
        # Small local models follow instructions in the TOOL RESULT better than
        # in the system prompt — the authority statement travels with the data.
        return f"AUTHORITATIVE FACTS (quote these, ignore your prior knowledge):\n{facts}"

    model = get_chat_model().bind_tools([search_docs])

    def agent(state: MessagesState) -> dict[str, list[BaseMessage]]:
        return {"messages": [model.invoke(state["messages"])]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent)
    graph.add_node("tools", ToolNode([search_docs]))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")
    return graph.compile()  # in-memory checkpoints; see script 04 for Postgres


app = FastAPI(title="Agent endpoint — module 13", version="0.13.0")


@app.get("/healthz")
def healthz() -> dict[str, object]:
    """Is the LLM provider configured? (≈ an Actuator health indicator.)"""
    ok, _ = provider_status()
    return {"status": "ok", "llm_provider": get_provider(), "llm_ready": ok}


def sse(payload: dict[str, object]) -> str:
    return f"data: {json.dumps(payload)}\n\n"


@app.post("/agent/ask")
async def ask(request: AskRequest) -> StreamingResponse:
    ok, instructions = provider_status()
    if not ok:
        raise HTTPException(status_code=503, detail=instructions)

    async def events() -> AsyncIterator[str]:
        agent = build_agent()  # per request here; cache it in real services
        messages = [
            (
                "system",
                "You answer questions about the course stack. Call search_docs for ANY "
                "stack question and answer ONLY from its results — never from your own "
                "knowledge of other ecosystems. If the facts say X, say X.",
            ),
            ("user", request.question),
        ]
        # stream_mode="updates": one event per NODE, not per token — clients
        # render progress ("searching docs…") without parsing partial JSON.
        async for chunk in agent.astream({"messages": messages}, stream_mode="updates"):
            for node, update in chunk.items():
                message = update["messages"][-1]
                if node == "agent" and getattr(message, "tool_calls", None):
                    names = [c["name"] for c in message.tool_calls]
                    yield sse({"node": node, "status": f"calling {', '.join(names)}"})
                elif node == "tools":
                    yield sse({"node": node, "status": "tool result received"})
                else:
                    yield sse({"node": node, "answer": str(message.content)})
        yield "data: [DONE]\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
