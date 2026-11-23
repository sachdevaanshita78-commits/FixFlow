from sqlalchemy import select
from security import hash_password
from database import SessionLocal
from models import Tenant, Ticket, User, UserRole

SAMPLE_TICKETS = {
    "BankCo": [
        ("Card charged twice", "I was charged twice for order 1234. Please refund the duplicate."),
        ("Transfer failed but money debited", "My UPI transfer failed but the amount left my account."),
        ("Cannot reset my password", "The reset link says it has expired every time I try."),
        ("Need account statement", "Please send my statement for the last three months."),
    ],
    "GovHelp": [
        ("Certificate application status", "I applied three weeks ago and have no update."),
        ("Wrong name on document", "My name is misspelled on the certificate I received."),
        ("Appointment rescheduling", "I need to move my appointment to next week."),
    ],
}


def main() -> None:
    with SessionLocal() as db:
        if db.scalar(select(Tenant.id).limit(1)) is not None:
            print("Database already has data, skipping seed.")
        else:
            for name, tickets in SAMPLE_TICKETS.items():
                tenant = Tenant(name=name)
                db.add(tenant)
                db.flush()  # assigns tenant.id

                slug = name.lower()
                # Placeholder hashes: real password hashing is added on Day 3
                db.add(User(tenant_id=tenant.id, email=f"admin@{slug}.test",
                            password_hash="AdminDev123!", role=UserRole.admin))
                db.add(User(tenant_id=tenant.id, email=f"agent@{slug}.test",
                            password_hash="AdminDev123!", role=UserRole.agent))

                for subject, body in tickets:
                    db.add(Ticket(tenant_id=tenant.id, subject=subject, body=body))
            db.commit()
            print("Seed data created.")

        print("\nTenants (copy an id for testing):")
        for tenant in db.scalars(select(Tenant).order_by(Tenant.name)).all():
            print(f"  {tenant.name}: {tenant.id}")


if __name__ == "__main__":
    main()