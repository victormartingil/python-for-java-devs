"""ORM model ≈ @Entity.

SQLAlchemy 2.0 style: type-annotated with Mapped[...] — mypy understands the
columns, and the mapped table is derived from the class. No XML, no annotations
processor; the class IS the mapping.

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn persistapp.main:app --reload   (from 10-persistence-sqlalchemy-alembic/)
"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from persistapp.database import Base


class TaskModel(Base):
    __tablename__ = "tasks"

    # Mapped[int] + primary_key ≈ @Id @GeneratedValue — SERIAL/IDENTITY in Postgres.
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    # Mapped[str | None] makes the column NULLABLE — the annotation drives the DDL.
    description: Mapped[str | None] = mapped_column(Text)
    completed: Mapped[bool] = mapped_column(default=False)
