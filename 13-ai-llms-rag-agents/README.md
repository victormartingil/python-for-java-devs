# 13 — AI: LLMs, RAG & agents

**The question this module answers:** *"What's the 2026 applied-AI stack — and what is each layer actually for?"* No hype, everything runnable, everything anchored to what you already know (Spring AI is the closest Java analogue, but the ecosystem's center of gravity is Python).

## The stack, in learning order

Each script adds exactly one concept. Run them in order — each is standalone and **degrades gracefully**: no API key and no Ollama → it prints setup instructions and exits 0. Nothing crashes.

| # | Script | Concept | Java anchor |
|---|---|---|---|
| 01 | `01_raw_sdk.py` | Raw OpenAI/Anthropic/Ollama SDK: messages, temperature, **structured outputs** validated with Pydantic | Calling the API with a bare `RestClient` |
| 02 | `02_langchain_lcel.py` | LangChain LCEL: `prompt \| model \| parser` chains | A fluent builder / Java Streams pipeline |
| 03 | `03_rag_pgvector.py` | Real RAG: chunk → embed → **pgvector** → context-stuffed prompt, with a minimal eval | A table + index queried with SQL — no new infra |
| 04 | `04_langgraph_agent.py` | LangGraph: agent = state machine; tool calling, agentic RAG, **Postgres checkpointer**, human-in-the-loop | A persisted workflow engine (Camunda/Temporal) where the LLM is an activity |
| 05 | `05_mcp_tools.py` | MCP client + server: the 2026 standard for exposing tools to agents | JDBC for AI tooling — one protocol, any driver |
| 06 | `06_agent_endpoint.py` | The agent as a FastAPI endpoint with **SSE streaming** | Your `@RestController` + `SseEmitter` |

*Requires: `uv sync --group web --group ai` (or `--all-groups`)*

```bash
uv run python 13-ai-llms-rag-agents/01_raw_sdk.py
# script 03 and 04's Postgres checkpointer need the pgvector container:
cd 13-ai-llms-rag-agents && docker compose up -d        # port 5433
```

## Why this order (and not "just use a framework")

1. **Raw SDK first** — an LLM call is a POST with a message list. Every framework abstraction sits on this; debugging requires knowing it.
2. **LCEL chains** — 80% of real LLM features (classify, extract, summarize, translate) are *one* call in a fixed pipeline. A chain is the right-sized tool; the `|` operator makes the dataflow explicit.
3. **RAG** — the moment the model needs *your* data: retrieve facts, stuff them into the prompt. pgvector because you already run Postgres — the demo is raw SQL (`ORDER BY embedding <=> CAST(:q AS vector)`) so you can see there is no magic, plus a one-line eval ("did the answer use the indexed docs?") because **unmeasured RAG is astrology**.
4. **LangGraph** — when the model must *decide*: call a tool? retrieve? loop? An agent is a loop; LangGraph makes the loop an explicit, persistable, interruptible graph. Checkpointer = durable execution (threads survive restarts, in Postgres you already have). `interrupt()` = human-in-the-loop in ~10 lines.
5. **MCP** — your tools shouldn't be framework-specific code. Expose them once as an MCP server; any agent/IDE consumes them. (Script 05's client/server roundtrip needs **no API key** — MCP is plumbing, not AI.)
6. **Ship it** — an agent is just another FastAPI dependency. SSE because token/graph streaming over plain HTTP beats WebSockets for one-way output.

## Providers: paid API or free local — one env var

All scripts get their model from `provider.py` (a factory ≈ switching a bean with a Spring profile):

```bash
LLM_PROVIDER=ollama      # default — free, local, private
LLM_PROVIDER=openai      # needs OPENAI_API_KEY
LLM_PROVIDER=anthropic   # needs ANTHROPIC_API_KEY
```

**Ollama setup (the free path):**

```bash
brew install ollama        # or https://ollama.com
ollama serve               # leave running in a terminal
ollama pull llama3.2 && ollama pull nomic-embed-text
```

Embeddings are separate: Anthropic has no embeddings API, so `get_embeddings()` picks OpenAI when keyed, else Ollama (`EMBEDDINGS_PROVIDER=openai|ollama` to force).

Two more knobs, same "Spring property override" idea:

```bash
OLLAMA_MODEL=qwen3.5:9b    # any pulled Ollama tag; default llama3.2
OLLAMA_HOST=http://gpu-box:11434   # remote Ollama; probe and client both honor it
```

**Live-verified 2026-07-23:** all six scripts ran end-to-end against a real Ollama (llama3.2 and qwen3.5:9b), `nomic-embed-text` embeddings and the pgvector container — RAG eval PASS, full agent loop with tool calling + human-in-the-loop, MCP roundtrip and SSE streaming. The test suite stays hermetic either way: it points the provider probe at a dead `OLLAMA_HOST` port, so it passes on machines with or without a live Ollama.

⚠️ **Cost warning.** Agents burn tokens: every loop iteration re-sends the conversation. The defaults are the cheap models (`gpt-4o-mini`, `claude-3-5-haiku`, local llama3.2). Do not point these scripts at a flagship model "to see what happens" — what happens is your invoice.

⚠️ **Small-model caveat — measured, not folklore.** Classifying the script 01 ticket ("charge after I cancelled my subscription"): llama3.2 (3B) says `technical`/`high`, qwen3.5:9b says `billing`/`medium` — the 9B is right. A 3B also occasionally ignores retrieved context; scripts 04/06 carry an "AUTHORITATIVE FACTS" hint in the tool result to compensate. With `gpt-4o-mini`+ the grounding is reliable. This is exactly why script 03 has an eval step.

## The agent frameworks landscape (2026)

| Framework | Pick it when | Trade-off |
|---|---|---|
| **LangGraph 1.x** | Production agents needing state, durability, human approval, fine control | More concepts to learn (graph thinking) |
| **Pydantic AI** | Type-safe single-agent tools with a "FastAPI feeling" | Less orchestration depth than LangGraph |
| **OpenAI Agents SDK** | You're all-in on OpenAI and want their hosted tracing/handoffs | Vendor lock-in by design |
| **CrewAI** | "Team of role-playing agents" demos; quick multi-agent prototypes | Abstraction leaks fast in production |
| **Google ADK** | Gemini-centric stacks, Google Cloud deployment | Young ecosystem, Google-shaped |

This repo teaches LangGraph because it covers the production case (Uber, Klarna, LinkedIn, Replit run it); the concepts (state, nodes, tools, checkpoints) transfer to all of the above.

**A2A (Agent2Agent) in 2 lines:** Google's protocol for agents calling *other agents* across orgs — where MCP standardizes agent↔tool, A2A standardizes agent↔agent. Complementary, not competing; watch it, don't build on it yet.

## Files

```
provider.py            # LLM_PROVIDER factory — the seam every script shares
docker-compose.yml     # pgvector/pgvector:pg16 on port 5433 (scripts 03, 04)
tests/                 # provider-factory unit tests + graceful-degradation proofs
                       # (all offline: no keys, no Ollama, no Docker)
```

Dependencies added to `pyproject.toml`: `openai`, `anthropic`, `langchain`, `langchain-openai/anthropic/ollama`, `langchain-text-splitters`, `langgraph`, `langgraph-checkpoint-postgres`, `pgvector`, `mcp`. All resolved cleanly with uv (lockfile pinned).

## Common pitfalls for Java devs

- **Treating the LLM as a function.** It's a nondeterministic service: validate everything it returns (Pydantic), temperature=0 for anything you test, and never put it inside a transaction boundary.
- **Reaching for an agent when a chain suffices.** If the flow has no decisions, an agent adds cost, latency and failure modes for nothing. Classify/extract/summarize = script 02, full stop.
- **Stuffing the whole document into the prompt.** Context is expensive and noisy; retrieval exists because 3 relevant chunks beat 300 pages. But chunk too small and you shred the meaning — 300–500 tokens with overlap is the sane default.
- **Letting the model answer from memory.** The entire point of RAG is that it can't. Put the grounding instruction *in the tool result* (script 04 shows why — small models obey data closer than system prompts).
- **Assuming MCP = plugins for one vendor.** It's a Linux Foundation protocol with first-party support from Anthropic, OpenAI, Google and Microsoft — the integration you write once.
- **Surprise bills in loops.** An agent that can loop can loop forever: cap iterations (`recursion_limit` in LangGraph), log token usage, use cheap models in dev.

## Dig deeper

- LangChain LCEL: <https://docs.langchain.com/oss/python/langchain/overview>
- LangGraph (durable execution, human-in-the-loop): <https://docs.langchain.com/oss/python/langgraph/overview>
- pgvector: <https://github.com/pgvector/pgvector>
- MCP spec: <https://modelcontextprotocol.io>
- Ollama: <https://ollama.com>
