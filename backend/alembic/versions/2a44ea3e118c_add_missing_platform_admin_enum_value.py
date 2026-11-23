"""add missing platform admin enum value

Revision ID: 2a44ea3e118c
Revises: 0d4439fa0ab1
Create Date: 2026-10-15 17:41:53.305049

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a44ea3e118c'
down_revision: Union[str, Sequence[str], None] = '0d4439fa0ab1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



"""Add missing platform admin enum value."""

from alembic import op

# Keep your generated revision and down_revision
# declarations exactly as they currently are.


def upgrade() -> None:
    op.execute(
        "ALTER TYPE public.user_role "
        "ADD VALUE IF NOT EXISTS 'platform_admin'"
    )


def downgrade() -> None:
    pass
