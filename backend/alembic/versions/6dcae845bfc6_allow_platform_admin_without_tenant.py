"""allow platform admin without tenant

Revision ID: 6dcae845bfc6
Revises: 2a44ea3e118c
Create Date: 2026-10-15 17:50:54.711813

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6dcae845bfc6'
down_revision: Union[str, Sequence[str], None] = '2a44ea3e118c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.alter_column(
        "users",
        "tenant_id",
        existing_type=sa.UUID(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "tenant_id",
        existing_type=sa.UUID(),
        nullable=False,
    )
