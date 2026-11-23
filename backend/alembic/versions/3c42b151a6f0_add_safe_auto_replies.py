"""add safe auto replies to tickets

Revision ID: 3c42b151a6f0
Revises: d41cb50c1161
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3c42b151a6f0"
down_revision: Union[str, Sequence[str], None] = "d41cb50c1161"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'new'")
    op.execute("ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'pending_agent'")
    op.execute("ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'auto_answered'")

    op.add_column(
        "tickets",
        sa.Column("reply", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tickets", "reply")

    op.execute("ALTER TABLE tickets ALTER COLUMN status DROP DEFAULT")
    op.execute(
        "CREATE TYPE ticket_status_old AS ENUM "
        "('open', 'in_progress', 'resolved')"
    )
    op.execute(
        "ALTER TABLE tickets ALTER COLUMN status TYPE ticket_status_old "
        "USING (CASE status::text "
        "WHEN 'auto_answered' THEN 'resolved' "
        "WHEN 'pending_agent' THEN 'open' "
        "WHEN 'new' THEN 'open' "
        "ELSE status::text END)::ticket_status_old"
    )
    op.execute("DROP TYPE ticket_status")
    op.execute("ALTER TYPE ticket_status_old RENAME TO ticket_status")
    op.execute(
        "ALTER TABLE tickets ALTER COLUMN status SET DEFAULT 'open'"
    )
