"""create tasks table

Revision ID: 0001
Revises:
Create Date: 2026-07-22

Hand-written for readability. In real work you'd generate this with:
    uv run alembic revision --autogenerate -m "create tasks table"
Alembic diffs Base.metadata (the models) against the live database and writes
the operations for you — then you review, exactly like checking a Flyway script.

Apply:    uv run alembic upgrade head
Rollback: uv run alembic downgrade -1
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("tasks")
