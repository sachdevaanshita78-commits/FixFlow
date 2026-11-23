
from sqlalchemy import select

from database import SessionLocal
from models import User, UserRole
from security import hash_password


EMAIL = "admin@gmail.com"


def create_platform_admin():
    with SessionLocal() as db:
        existing_user = db.scalar(
            select(User).where(User.email == EMAIL)
        )

        if existing_user:
            if existing_user.role == UserRole.platform_admin:
                print("This account is already a platform admin.")
                return

            print(
                f"Account {EMAIL} already exists with role "
                f"{existing_user.role.value}. No changes made."
            )
            return

        password = input("Create a password (minimum 12 characters): ")

        if len(password) < 12:
            print("Password must be at least 12 characters.")
            return

        user = User(
            tenant_id=None,
            full_name="Platform Administrator",
            email=EMAIL,
            password_hash=hash_password(password),
            role=UserRole.platform_admin,
        )

        db.add(user)
        db.commit()

        print(f"Created platform admin: {EMAIL}")


if __name__ == "__main__":
    create_platform_admin()
