
from sqlalchemy import select

from database import SessionLocal
from models import User
from security import hash_password

DEV_USERS = {
    "admin@bankco.test": "AdminDev123!",
    "agent@bankco.test": "AgentDev123!",
    "admin@govhelp.test": "AdminDev123!",
    "agent@govhelp.test": "AgentDev123!",
}


def main():
    with SessionLocal() as db:
        for email, password in DEV_USERS.items():
            user = db.scalar(
                select(User).where(User.email == email)
            )

            if user is None:
                print(f"User not found: {email}")
                continue

            user.password_hash = hash_password(password)
            print(f"Password hash updated: {email}")

        db.commit()


if __name__ == "__main__":
    main()
