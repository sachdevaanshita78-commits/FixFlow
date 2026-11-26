from sqlalchemy import select

from database import get_db
from models import Ticket, TicketStatus
from services.assignment import assign_ticket

db = next(get_db())

tickets = db.scalars(
    select(Ticket).where(
        Ticket.assigned_to_id.is_(None),
        Ticket.status.in_(
            [TicketStatus.new, TicketStatus.pending_agent, TicketStatus.open]
        ),
    )
).all()

for ticket in tickets:
    employee = assign_ticket(db, ticket)
    category = str(ticket.category or "NO CATEGORY")
    assignee = employee.full_name if employee else "NOT ASSIGNED"
    print(f"{str(ticket.id)[:8]}  {category:<16} -> {assignee}")

db.commit()
print(f"Processed {len(tickets)} ticket(s).")