"""03 — Real RAG: chunk → embed → pgvector → context-stuffed prompt.

RAG (Retrieval-Augmented Generation) in one sentence: look up the relevant
facts in YOUR data first, paste them into the prompt, then ask. The model
answers from the retrieved context instead of hallucinating.

Vector store: pgvector on the Postgres you already know — no new
infrastructure, no Chroma/Pinecone for a course project. The heavy lifting
is one SQL operator you can read:

    ORDER BY embedding <=> :query_vector   -- cosine distance, smaller = closer

Java anchor: this is a plain table + an index type, queried with SQL —
closer to a full-text GIN index than to a new database product.

Needs: the pgvector container (docker-compose.yml in this directory) and an
embeddings provider. Missing either? The script prints instructions, exits 0.

Run:  cd 13-ai-llms-rag-agents && docker compose up -d
      uv run python 13-ai-llms-rag-agents/03_rag_pgvector.py
"""

import asyncio
import os
import socket
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

from langchain_text_splitters import RecursiveCharacterTextSplitter
from provider import get_chat_model, get_embeddings, provider_status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = os.environ.get(
    "RAG_DATABASE_URL", "postgresql+asyncpg://tasks:tasks@localhost:5433/rag"
)

# The "knowledge base": facts the base model does NOT reliably know.
DOCUMENTS = {
    "packaging.md": (
        "In this course's stack, uv replaces pip, venv, pyenv and Poetry. "
        "Dependencies live in pyproject.toml and are locked in uv.lock. "
        "Run anything with 'uv run', add packages with 'uv add'."
    ),
    "di.md": (
        "FastAPI dependency injection uses Depends() instead of @Autowired. "
        "The composition root is a dependencies.py module where every concrete "
        "class is constructed. Tests swap implementations via app.dependency_overrides."
    ),
    "persistence.md": (
        "The course persists with SQLAlchemy 2.0 in async mode over asyncpg, "
        "with Alembic for migrations — the Flyway equivalent. Repositories are "
        "Protocol-shaped so services never import SQLAlchemy."
    ),
    "testing.md": (
        "The test pyramid puts pure service tests at the bottom, API tests with "
        "in-memory repositories in the middle, and testcontainers repository tests "
        "against real PostgreSQL at the top. Mocks are reserved for external services."
    ),
    "deployment.md": (
        "Production runs gunicorn with uvicorn workers behind a proxy, with "
        "workers set to 2 times CPU count plus 1. Images are multi-stage Docker "
        "builds using the official Astral uv image."
    ),
}

QUESTION = "How do I add a new dependency in this stack, and where is it locked?"
EXPECTED_KEYWORD = "uv"  # minimal evaluation: the answer MUST come from the docs


def db_reachable() -> bool:
    parsed = urlparse(DATABASE_URL.replace("+asyncpg", ""))
    try:
        with socket.create_connection((parsed.hostname or "localhost", parsed.port or 5432), 0.5):
            return True
    except OSError:
        return False


async def main() -> None:
    ok, instructions = provider_status()
    if not ok:
        print(f"LLM provider not ready.\n\n{instructions}")
        return
    if not db_reachable():
        print(
            "pgvector database not reachable.\n\n"
            "  cd 13-ai-llms-rag-agents && docker compose up -d\n"
            "  (image: pgvector/pgvector:pg16 — Postgres 16 with the extension preinstalled)"
        )
        return

    # 1. CHUNK — split documents so retrieval can pinpoint the relevant piece.
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    chunks = [
        (source, chunk) for source, doc in DOCUMENTS.items() for chunk in splitter.split_text(doc)
    ]
    print(f"1. Chunking: {len(DOCUMENTS)} documents → {len(chunks)} chunks")

    # 2. EMBED — one vector per chunk. Dimensions depend on the provider's model.
    embeddings = get_embeddings()
    vectors = await embeddings.aembed_documents([chunk for _, chunk in chunks])
    dim = len(vectors[0])
    print(f"2. Embeddings: {len(vectors)} vectors × {dim} dimensions")

    # 3. STORE — a plain table with a vector column. Fresh per run (demo, not prod).
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.execute(text("DROP TABLE IF EXISTS rag_chunks"))
        await conn.execute(
            text(
                f"CREATE TABLE rag_chunks ("
                f" id bigserial PRIMARY KEY, source text, content text, embedding vector({dim}))"
            )
        )
        for (source, chunk), vector in zip(chunks, vectors, strict=True):
            await conn.execute(
                # CAST(... AS vector): asyncpg turns :param into $n; writing the
                # cast as :param::vector would confuse SQLAlchemy's text() lexer.
                text(
                    "INSERT INTO rag_chunks (source, content, embedding)"
                    " VALUES (:source, :content, CAST(:embedding AS vector))"
                ),
                {"source": source, "content": chunk, "embedding": str(vector)},
            )
    print("3. Stored in pgvector (table rag_chunks)")

    # 4. RETRIEVE — embed the question, ask SQL for the nearest chunks.
    query_vector = (await embeddings.aembed_query(QUESTION)).__str__()
    async with engine.connect() as conn:
        rows = (
            await conn.execute(
                text(
                    "SELECT source, content, embedding <=> CAST(:q AS vector) AS distance"
                    " FROM rag_chunks ORDER BY distance LIMIT 3"
                ),
                {"q": query_vector},
            )
        ).all()
    await engine.dispose()
    print("4. Retrieved (cosine distance):")
    for source, _, distance in rows:
        print(f"   {distance:.4f}  {source}")

    # 5. GENERATE — stuff the context into the prompt; the model reads, not recalls.
    context = "\n\n".join(f"[{source}]\n{content}" for source, content, _ in rows)
    prompt = (
        "Answer ONLY from the context below. If the answer is not there, say so.\n\n"
        f"Context:\n{context}\n\nQuestion: {QUESTION}"
    )
    answer = await get_chat_model().ainvoke(prompt)
    answer_text = str(answer.content)
    print(f"5. Answer: {answer_text}\n")

    # 6. MINIMAL EVALUATION — did it answer from the indexed docs?
    grounded = EXPECTED_KEYWORD.lower() in answer_text.lower() and "packaging" in rows[0][0]
    print(
        f"6. Eval: expected keyword {EXPECTED_KEYWORD!r} in answer and top hit "
        f"from packaging.md → {'PASS' if grounded else 'FAIL'}"
    )


if __name__ == "__main__":
    asyncio.run(main())
