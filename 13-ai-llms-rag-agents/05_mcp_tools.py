"""05 — MCP (Model Context Protocol): the USB-C port for agent tools.

The problem: every agent framework × every tool/database/API used to be a
custom integration (N frameworks × M tools). MCP — donated to the Linux
Foundation, adopted by Anthropic, OpenAI, Google and Microsoft — is the 2026
standard that ends that: a tool/data source is exposed ONCE as an MCP server;
any MCP-capable agent or IDE can discover and call it.

Java anchor: think JDBC for AI tooling — one protocol, any driver. The
server exposes TOOLS (callable functions), RESOURCES (readable data) and
PROMPTS; the client discovers them at runtime (list_tools) instead of
hardcoding schemas.

This script is BOTH halves:
    python 05_mcp_tools.py --serve   → stdio MCP server (what an agent spawns)
    python 05_mcp_tools.py           → MCP client: connects, lists tools,
                                       calls one — then hands the result to
                                       the LLM if a provider is configured

The client/server roundtrip needs NO API key — MCP is plumbing, not AI.

Run:  uv run python 13-ai-llms-rag-agents/05_mcp_tools.py
"""

import asyncio
import sys
from collections.abc import Sequence
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp.server.fastmcp import FastMCP

COURSE_FACTS = {
    "uv": "uv replaces pip/venv/Poetry; uv.lock pins the whole dependency tree.",
    "fastapi": "FastAPI uses Depends() for DI and Pydantic for validation.",
    "alembic": "Alembic autogenerates migrations from SQLAlchemy models — the Flyway of Python.",
    "testing": (
        "Repositories are tested against real Postgres via testcontainers; "
        "external APIs are mocked."
    ),
}

# ---------------------------------------------------------------- server side
mcp_server = FastMCP("course-tools")


@mcp_server.tool()
def count_words(text: str) -> int:
    """Count the words in a text. Deterministic — no LLM involved."""
    return len(text.split())


@mcp_server.tool()
def lookup_course_fact(topic: str) -> str:
    """Look up a fact about the python-for-java-devs stack by keyword."""
    for keyword, fact in COURSE_FACTS.items():
        if keyword in topic.lower():
            return fact
    return f"No fact found for {topic!r}. Known keywords: {', '.join(COURSE_FACTS)}"


# ---------------------------------------------------------------- client side
def first_text(content: Sequence[object]) -> str:
    """A tool result is a list of content blocks (text, image, ...) — take the text."""
    from mcp.types import TextContent

    for block in content:
        if isinstance(block, TextContent):
            return block.text
    return ""


async def client_demo() -> None:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    # The client SPAWNS the server as a subprocess and talks JSON-RPC over stdio —
    # exactly how Claude Desktop / an agent runtime launches local MCP servers.
    params = StdioServerParameters(
        command=sys.executable, args=[str(Path(__file__).resolve()), "--serve"]
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Runtime discovery — the agent learns the tool schemas FROM the server.
            tools = await session.list_tools()
            print("Tools discovered via MCP:")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description.splitlines()[0] if t.description else ''}")

            fact = await session.call_tool("lookup_course_fact", {"topic": "uv"})
            fact_text = first_text(fact.content)
            count = await session.call_tool("count_words", {"text": fact_text})
            count_text = first_text(count.content)
            print(f"\nlookup_course_fact('uv') → {fact_text}")
            print(f"count_words(fact)         → {count_text} words")

    # Optional: hand the tool result to an LLM (needs a provider — skipped offline).
    from provider import get_chat_model, get_provider, provider_status

    ok, instructions = provider_status()
    if not ok:
        print(f"\n(LLM step skipped — {instructions.splitlines()[0]})")
        print("MCP roundtrip above needed no API key: MCP is plumbing, not AI.")
        return
    model = get_chat_model()
    answer = model.invoke(
        f"Answer in one sentence using ONLY this fact: {fact_text}\n"
        "Question: what pins the dependency tree in this stack?"
    )
    print(f"\nLLM grounded on the MCP tool result ({get_provider()}): {answer.content}")


def main() -> None:
    if "--serve" in sys.argv:
        mcp_server.run()  # stdio transport: stdin/stdout JSON-RPC until killed
        return
    asyncio.run(client_demo())


if __name__ == "__main__":
    main()
