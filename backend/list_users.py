from sqlalchemy import select
from database import SessionLocal
from models import User

with SessionLocal() as db:
    users = db.scalars(
        select(User).order_by(User.email)
    ).all()

    if not users:
        print("No users found.")

    for user in users:
        print(
            f"Email: {user.email} | "
            f"Role: {user.role.value} | "
            f"Tenant ID: {user.tenant_id}"
        )
