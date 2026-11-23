from sqlalchemy import func, select

from database import SessionLocal
from models import Tenant, Ticket, TicketStatus

with SessionLocal() as db:
    # 1. JOIN + GROUP BY: how many tickets does each tenant have?
    rows = db.execute(
        select(Tenant.name, func.count(Ticket.id))
        .join(Ticket, Ticket.tenant_id == Tenant.id)
        .group_by(Tenant.name)
    ).all()
    print("Tickets per tenant:")
    for name, count in rows:
        print(f"  {name}: {count}")

    # 2. Tenant isolation: only BankCo's tickets
    bank = db.scalar(select(Tenant).where(Tenant.name == "BankCo"))
    tickets = db.scalars(select(Ticket).where(Ticket.tenant_id == bank.id)).all()
    print(f"\nBankCo ticket subjects ({len(tickets)}):")
    for t in tickets:
        print(f"  - {t.subject} [{t.status.value}]")

    # 3. Filter by status
    open_count = db.scalar(
        select(func.count(Ticket.id)).where(
            Ticket.tenant_id == bank.id, Ticket.status == TicketStatus.open
        )
    )
    print(f"\nBankCo open tickets: {open_count}")