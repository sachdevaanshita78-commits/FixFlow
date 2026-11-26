
"""add categories to users

Revision ID: b90e74fd2239
Revises: 7ef6d830216e
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "b90e74fd2239"
down_revision: Union[str, Sequence[str], None] = "7ef6d830216e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "categories",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )

    op.alter_column(
        "users",
        "categories",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("users", "categories")
