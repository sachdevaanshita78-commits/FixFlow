from sqlalchemy import text
from database import engine

with engine.connect() as connection:
    database_info = connection.execute(
        text("SELECT current_database(), current_schema()")
    ).one()

    print("Database:", database_info[0])
    print("Schema:", database_info[1])

    result = connection.execute(text("""
        SELECT n.nspname, t.typname, e.enumlabel
        FROM pg_type t
        JOIN pg_enum e ON e.enumtypid = t.oid
        JOIN pg_namespace n ON n.oid = t.typnamespace
        WHERE t.typname = 'user_role'
        ORDER BY e.enumsortorder
    """))

    print("\nRegistered user_role values:")
    for row in result:
        print(f"{row[0]}.{row[1]} -> {row[2]}")
