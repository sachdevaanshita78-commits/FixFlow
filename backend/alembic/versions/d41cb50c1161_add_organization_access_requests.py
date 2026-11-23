
"""add organization access requests

Revision ID: d41cb50c1161
Revises: d205019c8c19
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d41cb50c1161"
down_revision: Union[str, Sequence[str], None] = "d205019c8c19"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the organization access requests table."""

    op.create_table(
        "organization_access_requests",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_name", sa.String(length=120), nullable=False),
        sa.Column("admin_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default="pending",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_organization_access_requests_email",
        "organization_access_requests",
        ["email"],
        unique=False,
    )


def downgrade() -> None:
    """Remove the organization access requests table."""

    op.drop_index(
        "ix_organization_access_requests_email",
        table_name="organization_access_requests",
    )
    op.drop_table("organization_access_requests")
