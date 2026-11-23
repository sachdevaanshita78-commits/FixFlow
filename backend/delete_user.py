
from sqlalchemy import delete, select
from database import SessionLocal
from models import User

email = input("Enter employee email to delete: ").strip().lower()

with SessionLocal() as db:
    user = db.scalars(
        select(User).where(User.email == email)
    ).first()

    if not user:
        print("User not found.")
    elif user.role.value == "platform_admin":
        print("Cannot delete the platform admin with this script.")
    else:
        print(f"Email: {user.email}")
        print(f"Role: {user.role.value}")
        print(f"Tenant ID: {user.tenant_id}")

        confirm = input("Type DELETE to confirm: ").strip()

        if confirm == "DELETE":
            db.execute(delete(User).where(User.id == user.id))
            db.commit()
            print("User deleted successfully.")
        else:
            print("Deletion cancelled.")
