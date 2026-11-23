from sqlalchemy import delete, select
from database import SessionLocal
from models import Invitation


email = input("Enter the recipient email: ").strip()
tenant_id = input("Enter the tenant UUID: ").strip()

with SessionLocal() as db:
    query = select(Invitation).where(
        Invitation.email == email,
        Invitation.tenant_id == tenant_id,
        Invitation.accepted_at.is_(None),
    )

    invitations = db.scalars(query).all()

    if not invitations:
        print("No matching pending invitation found.")
    else:
        print(f"\nFound {len(invitations)} pending invitation(s):")

        for invitation in invitations:
            print(
                f"ID: {invitation.id} | "
                f"Email: {invitation.email} | "
                f"Expires: {invitation.expires_at}"
            )

        confirm = input(
            "\nType DELETE to permanently delete these invitations: "
        ).strip()

        if confirm == "DELETE":
            db.execute(
                delete(Invitation).where(
                    Invitation.email == email,
                    Invitation.tenant_id == tenant_id,
                    Invitation.accepted_at.is_(None),
                )
            )
            db.commit()
            print("Invitation deleted successfully.")
        else:
            print("Deletion cancelled.")