"""add full name to users

Revision ID: 16313d64531c
Revises: 80f080244ba2
Create Date: 2026-10-15 13:35:57.168440

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '16313d64531c'
down_revision: Union[str, Sequence[str], None] = '80f080244ba2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.execute(
        "ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'platform_admin'"
    )


def downgrade() -> None:
    # PostgreSQL does not support removing an enum value directly.
    # Keep the value rather than risking existing user data.
    pass
