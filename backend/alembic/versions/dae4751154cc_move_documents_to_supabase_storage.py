
"""move documents to supabase storage

Revision ID: dae4751154cc
Revises: 7a193deb64e5
Create Date: 2026-10-16 18:37:30.144051
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "dae4751154cc"
down_revision: Union[str, Sequence[str], None] = "7a193deb64e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("storage_path", sa.String(length=500), nullable=True),
    )

    op.create_unique_constraint(
        "uq_documents_storage_path",
        "documents",
        ["storage_path"],
    )

    op.drop_column("documents", "content")

    op.alter_column(
        "documents",
        "storage_path",
        existing_type=sa.String(length=500),
        nullable=False,
    )

def downgrade() -> None:
    """Restore the previous document schema."""

    op.add_column(
        "documents",
        sa.Column("content", sa.Text(), nullable=True),
    )

    op.drop_constraint(
        "ck_documents_storage_path_present",
        "documents",
        type_="check",
    )

    op.drop_constraint(
        "uq_documents_storage_path",
        "documents",
        type_="unique",
    )

    op.drop_column("documents", "storage_path")

    # Restore the old column's NOT NULL requirement.
    op.alter_column(
        "documents",
        "content",
        existing_type=sa.Text(),
        nullable=False,
    )
