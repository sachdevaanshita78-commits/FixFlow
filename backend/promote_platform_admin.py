
from sqlalchemy import select

from database import SessionLocal
from models import User, UserRole


def promote_user(email: str) -> None:
    with SessionLocal() as db:
        user = db.scalar(
            select(User).where(User.email == email.strip().lower())
        )

        if user is None:
            print("User not found. No changes made.")
            return

        user.role = UserRole.platform_admin
        db.commit()

        print(f"Promoted {user.email} to platform_admin.")


if __name__ == "__main__":
    email = input("Enter the trusted platform admin email: ").strip()
    confirm = input(
        f"Promote {email} to platform_admin? Type YES to confirm: "
    )

    if confirm == "YES":
        promote_user(email)
    else:
        print("Cancelled. No changes made.")
