
"""add employee categories relationship

Revision ID: 4093d415fc4c
Revises: b90e74fd2239
Create Date: 2026-11-24 19:39:34.619117
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "4093d415fc4c"
down_revision: Union[str, Sequence[str], None] = "b90e74fd2239"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create the employee-category association table.
    op.create_table(
        "employee_categories",
        sa.Column("employee_id", sa.UUID(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("employee_id", "category"),
    )

    # 2. Migrate existing categories from JSONB into the new table.
    op.execute("""
        INSERT INTO employee_categories (employee_id, category)
        SELECT
            users.id,
            jsonb_array_elements_text(users.categories)
        FROM users
        WHERE users.categories IS NOT NULL
          AND jsonb_typeof(users.categories) = 'array'
        ON CONFLICT DO NOTHING;
    """)

    # 3. Drop the old JSONB column after migrating its data.
    op.drop_column("users", "categories")


def downgrade() -> None:
    # Restore the original categories column.
    op.add_column(
        "users",
        sa.Column(
            "categories",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )

    # Restore category values from the association table.
    op.execute("""
        UPDATE users
        SET categories = COALESCE(
            (
                SELECT jsonb_agg(employee_categories.category)
                FROM employee_categories
                WHERE employee_categories.employee_id = users.id
            ),
            '[]'::jsonb
        );
    """)

    # Remove the temporary server default.
    op.alter_column(
        "users",
        "categories",
        server_default=None,
    )

    op.drop_table("employee_categories")