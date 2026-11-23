
"""add document file size

Revision ID: d205019c8c19
Revises: dae4751154cc
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d205019c8c19"
down_revision: Union[str, Sequence[str], None] = "dae4751154cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("file_size", sa.Integer(), nullable=False, server_default="0"),
    )
    op.alter_column(
        "documents",
        "file_size",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("documents", "file_size")
