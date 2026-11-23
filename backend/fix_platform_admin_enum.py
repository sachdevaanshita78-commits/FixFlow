
from sqlalchemy import text
from database import engine

with engine.begin() as connection:
    connection.execute(
        text(
            "ALTER TYPE public.user_role "
            "ADD VALUE IF NOT EXISTS 'platform_admin'"
        )
    )

print("Enum update executed.")
