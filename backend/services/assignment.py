import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models import (
    EmployeeCategory,
    Ticket,
    TicketStatus,
    User,
    UserRole,
)

logger = logging.getLogger("fixflow")

ACTIVE_STATUSES = [
    TicketStatus.new,
    TicketStatus.pending_agent,
    TicketStatus.open,
    TicketStatus.in_progress,
]

GENERAL_CATEGORY = "OTHER"


def _least_loaded(db: Session, tenant_id, candidates: list[User]) -> User:
    """Pick the candidate with the fewest active tickets (ties: oldest account)."""
    candidate_ids = [employee.id for employee in candidates]

    rows = db.execute(
        select(Ticket.assigned_to_id, func.count(Ticket.id))
        .where(
            Ticket.tenant_id == tenant_id,
            Ticket.assigned_to_id.in_(candidate_ids),
            Ticket.status.in_(ACTIVE_STATUSES),
        )
        .group_by(Ticket.assigned_to_id)
    ).all()

    workloads = {employee_id: count for employee_id, count in rows}

    return min(
        candidates,
        key=lambda employee: (
            workloads.get(employee.id, 0),
            employee.created_at,
            str(employee.id),
        ),
    )


def assign_ticket(db: Session, ticket: Ticket):
    agents_query = select(User).where(
        User.tenant_id == ticket.tenant_id,
        User.role == UserRole.agent,
    )

    candidates: list[User] = []

    # 1. Agents who support this ticket's category.
    if ticket.category and ticket.category != GENERAL_CATEGORY:
        candidates = db.scalars(
            agents_query.join(
                EmployeeCategory,
                EmployeeCategory.employee_id == User.id,
            ).where(EmployeeCategory.category == ticket.category)
        ).all()

    # 2. General tickets, or no category specialist: any agent.
    if not candidates:
        candidates = db.scalars(agents_query).all()

    # 3. No agents at all: fall back to the company admin.
    if not candidates:
        candidates = db.scalars(
            select(User).where(
                User.tenant_id == ticket.tenant_id,
                User.role == UserRole.admin,
            )
        ).all()

    if not candidates:
        logger.warning("No one available to assign ticket %s to", ticket.id)
        ticket.assigned_to_id = None
        return None

    selected = _least_loaded(db, ticket.tenant_id, candidates)
    ticket.assigned_to_id = selected.id

    return selected
