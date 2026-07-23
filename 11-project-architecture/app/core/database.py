"""Engine, session factory and declarative Base (≈ DataSource + EntityManagerFactory).

Same SQLAlchemy 2.0 async pattern as module 10, promoted to core/ because
every domain module shares it.

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn app.main:app --reload   (from 11-project-architecture/)
"""

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Every ORM model in every domain module inherits from this one Base —
    so Alembic sees the whole schema in one metadata."""


engine = create_async_engine(get_settings().database_url)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
