"""Engine + session factory ≈ DataSource + EntityManagerFactory.

- AsyncEngine:      the connection pool (≈ HikariCP DataSource)
- AsyncSession:     the unit of work / persistence context (≈ EntityManager)
- Base:             the declarative base every ORM model inherits from
- get_session:      one session per request via Depends (≈ OpenSessionInView),
                    committing on success, rolling back on any exception

Nothing connects at import time — creating an engine is lazy (like a DataSource).

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn persistapp.main:app --reload   (from 10-persistence-sqlalchemy-alembic/)
"""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from persistapp.config import get_settings


class Base(DeclarativeBase):
    """≈ the common mapped superclass. Alembic reads Base.metadata to know the schema."""


engine = create_async_engine(get_settings().database_url)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Request-scoped session with a transaction around the endpoint.

    yield ≈ open session + begin tx; code after yield ≈ commit (or rollback
    if the endpoint raised). FastAPI runs the teardown after the endpoint returns.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
