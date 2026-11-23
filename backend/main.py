import hashlib
import logging
import secrets
import uuid
import os

from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from sqlalchemy import delete
from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordRequestForm,
)

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import get_db
from models import (
    User,
    Tenant,
    Ticket,
    Draft,
    Document,
    Invitation,
    UserRole,
    TicketStatus,
    OrganizationAccessRequest,
)
from schemas import (
    TokenResponse,
    TenantOut,
    TicketCreate,
    TicketIntakeOut,
    TicketOut,
    TicketUpdate,
    InvitationCreate,
    InvitationAccept,
    AIAnswerRequest,
    AIAnswerOut,
    OrganizationRegister,
)
from security import (
    create_access_token,
    verify_password,
    get_current_user,
    require_admin,
    require_platform_admin,
    hash_password,
)
from email_service import send_invitation_email
from supabase_client import supabase, SUPABASE_BUCKET
from rag_service import (
    answer_question,
    index_document,
    delete_document_vectors,
    reply_requires_internal_action,
    warmup_embedding_model,
)

# ==================================================
# APPLICATION
# ==================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fixflow")

# Aurora Bank server-to-server integration
AURORA_INTEGRATION_KEY = os.getenv("AURORA_INTEGRATION_KEY")
AURORA_TENANT_ID = os.getenv("AURORA_TENANT_ID")
aurora_bearer = HTTPBearer(auto_error=False)


def verify_aurora_integration(
    credentials: HTTPAuthorizationCredentials | None = Depends(aurora_bearer),
):
    if not AURORA_INTEGRATION_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Aurora integration is not configured",
        )

    if credentials is None or not secrets.compare_digest(
        credentials.credentials, AURORA_INTEGRATION_KEY
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid integration credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not AURORA_TENANT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Aurora tenant is not configured",
        )

    try:
        return uuid.UUID(AURORA_TENANT_ID)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Aurora tenant configuration is invalid",
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the embedding model once at startup, not on the first ticket."""
    try:
        warmup_embedding_model()
        logger.info("Embedding model is ready")
    except Exception:
        logger.exception("Embedding model warm-up failed")
    yield


app = FastAPI(
    title="FixFlow API",
    version="1.0.0",
    description="Multi-tenant AI customer support platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# CONSTANTS
# ==================================================

MAX_DOCUMENT_SIZE = 10 * 1024 * 1024

ALLOWED_DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
}

DOCUMENT_CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".docx": (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document"
    ),
    ".txt": "text/plain",
    ".md": "text/markdown",
}


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def require_tenant_user(current_user: User) -> uuid.UUID:
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This operation requires a tenant account",
        )

    return current_user.tenant_id


def require_company_admin(current_user: User) -> uuid.UUID:
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company administrators can manage documents",
        )

    return require_tenant_user(current_user)


def get_ticket_or_404(
    db: Session,
    tenant_id: uuid.UUID,
    ticket_id: uuid.UUID,
) -> Ticket:
    ticket = db.scalar(
        select(Ticket).where(
            Ticket.id == ticket_id,
            Ticket.tenant_id == tenant_id,
        )
    )

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return ticket


def get_document_or_404(
    db: Session,
    tenant_id: uuid.UUID,
    document_id: uuid.UUID,
) -> Document:
    document = db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.tenant_id == tenant_id,
        )
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


def document_response(document: Document) -> dict:
    return {
        "id": str(document.id),
        "title": document.title,
        "filename": document.filename,
        "file_size": document.file_size,
        "created_at": document.created_at,
    }


def remove_storage_object(storage_path: str) -> None:
    """Remove an object from the configured private Supabase bucket."""
    supabase.storage.from_(SUPABASE_BUCKET).remove([storage_path])


# ==================================================
# HEALTH CHECKS
# ==================================================

@app.get("/")
def root():
    return {
        "message": "Welcome to FixFlow API",
        "docs": "/docs",
    }


@app.get("/health/live")
def health_live():
    return {"status": "alive"}


@app.get("/health/ready")
def health_ready(db: Session = Depends(get_db)):
    try:
        db.execute(select(1))
        return {
            "status": "ready",
            "database": "connected",
        }
    except Exception as exc:
        logger.exception("Database readiness check failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        ) from exc


# ==================================================
# AUTHENTICATION
# ==================================================

@app.post(
    "/api/v1/auth/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(User.email == form_data.username)
    )

    if user is None or not verify_password(
        form_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ==================================================
# PUBLIC ORGANIZATION REGISTRATION
# ==================================================

@app.post(
    "/api/v1/auth/register-organization",
    status_code=status.HTTP_201_CREATED,
)
def register_organization(
    organization: OrganizationRegister,
    db: Session = Depends(get_db),
):
    email = str(organization.email).strip().lower()
    company_name = organization.company_name.strip()
    admin_name = organization.admin_name.strip()

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    existing_request = db.scalar(
        select(OrganizationAccessRequest).where(
            OrganizationAccessRequest.email == email,
            OrganizationAccessRequest.status == "pending",
        )
    )

    if existing_request is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pending request already exists for this email.",
        )

    existing_tenant = db.scalar(
        select(Tenant).where(Tenant.name == company_name)
    )

    if existing_tenant is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An organization with this name already exists.",
        )

    request = OrganizationAccessRequest(
        company_name=company_name,
        admin_name=admin_name,
        email=email,
        password_hash=hash_password(organization.password),
        status="pending",
    )

    try:
        db.add(request)
        db.commit()
        db.refresh(request)

        return {
            "message": "Registration request submitted for approval.",
            "request_id": str(request.id),
            "status": request.status,
        }

    except Exception:
        db.rollback()
        logger.exception("Organization registration request failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to submit the registration request.",
        )


# ==================================================
# PLATFORM ADMIN: ORGANIZATION REQUESTS
# ==================================================

@app.get("/api/v1/platform/organization-requests")
def list_organization_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
):
    requests = db.scalars(
        select(OrganizationAccessRequest).order_by(
            OrganizationAccessRequest.created_at.desc()
        )
    ).all()

    return [
        {
            "id": str(request.id),
            "company_name": request.company_name,
            "admin_name": request.admin_name,
            "email": request.email,
            "status": request.status,
            "created_at": request.created_at,
        }
        for request in requests
    ]


@app.post(
    "/api/v1/platform/organization-requests/{request_id}/approve"
)
def approve_organization_request(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
):
    request = db.get(OrganizationAccessRequest, request_id)

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization request not found.",
        )

    if request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This request has already been reviewed.",
        )

    existing_user = db.scalar(
        select(User).where(User.email == request.email)
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    existing_tenant = db.scalar(
        select(Tenant).where(Tenant.name == request.company_name)
    )

    if existing_tenant is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An organization with this name already exists.",
        )

    try:
        tenant = Tenant(name=request.company_name)
        db.add(tenant)
        db.flush()

        admin_user = User(
            tenant_id=tenant.id,
            full_name=request.admin_name,
            email=request.email,
            password_hash=request.password_hash,
            role=UserRole.admin,
        )

        db.add(admin_user)
        request.status = "approved"

        db.commit()
        db.refresh(tenant)

        return {
            "message": "Organization approved successfully.",
            "tenant_id": str(tenant.id),
            "company_name": tenant.name,
            "admin_email": admin_user.email,
            "status": request.status,
        }

    except Exception:
        db.rollback()
        logger.exception("Organization approval failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to approve the organization request.",
        )


@app.post(
    "/api/v1/platform/organization-requests/{request_id}/reject"
)
def reject_organization_request(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
):
    request = db.get(OrganizationAccessRequest, request_id)

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization request not found.",
        )

    if request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This request has already been reviewed.",
        )

    try:
        request.status = "rejected"
        db.commit()

        return {
            "message": "Organization request rejected.",
            "request_id": str(request.id),
            "status": request.status,
        }

    except Exception:
        db.rollback()
        logger.exception("Organization request rejection failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to reject the organization request.",
        )


# ==================================================
# CURRENT USER
# ==================================================

@app.get("/api/v1/auth/me")
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tenant = (
        db.get(Tenant, current_user.tenant_id)
        if current_user.tenant_id
        else None
    )

    return {
        "id": str(current_user.id),
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role.value,
        "tenant_id": (
            str(current_user.tenant_id)
            if current_user.tenant_id
            else None
        ),
        "company_name": tenant.name if tenant else None,
    }


# ==================================================
# ORGANIZATIONS / TENANTS
# ==================================================

@app.get(
    "/api/v1/tenants",
    response_model=list[TenantOut],
)
def list_tenants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.platform_admin:
        tenants = db.scalars(
            select(Tenant).order_by(Tenant.created_at.desc())
        ).all()

        results = []

        for tenant in tenants:
            owner = db.scalar(
                select(User)
                .where(
                    User.tenant_id == tenant.id,
                    User.role == UserRole.admin,
                )
                .order_by(User.email)
            )

            results.append({
                "id": tenant.id,
                "name": tenant.name,
                "created_at": tenant.created_at,
                "owner_email": owner.email if owner else None,
            })

        return results

    tenant_id = require_tenant_user(current_user)

    return db.scalars(
        select(Tenant).where(Tenant.id == tenant_id)
    ).all()


@app.post(
    "/api/v1/tenants",
    response_model=TenantOut,
    status_code=status.HTTP_201_CREATED,
)
def create_tenant(
    organization: OrganizationRegister,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
):
    existing_user = db.scalar(
        select(User).where(User.email == organization.email)
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    existing_tenant = db.scalar(
        select(Tenant).where(
            Tenant.name == organization.company_name
        )
    )

    if existing_tenant is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An organization with this name already exists",
        )

    try:
        tenant = Tenant(name=organization.company_name)
        db.add(tenant)
        db.flush()

        admin_user = User(
            tenant_id=tenant.id,
            full_name=organization.admin_name,
            email=str(organization.email),
            password_hash=hash_password(organization.password),
            role=UserRole.admin,
        )

        db.add(admin_user)
        db.commit()
        db.refresh(tenant)

        return {
            "id": tenant.id,
            "name": tenant.name,
            "created_at": tenant.created_at,
            "owner_email": admin_user.email,
        }

    except Exception:
        db.rollback()
        logger.exception("Organization creation failed")
        raise


# ==================================================
# COMPANY EMPLOYEES
# ==================================================

@app.get("/api/v1/tenants/users")
def list_company_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    tenant_id = require_tenant_user(current_user)

    users = db.scalars(
        select(User)
        .where(
            User.tenant_id == tenant_id,
            User.role != UserRole.platform_admin,
        )
        .order_by(User.created_at.desc())
    ).all()

    return [
        {
            "id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role.value,
            "tenant_id": str(user.tenant_id),
            "created_at": user.created_at,
        }
        for user in users
    ]


# ==================================================
# PLATFORM METRICS
# ==================================================

@app.get("/api/v1/platform/metrics")
def get_platform_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
):
    """Return aggregate platform metrics, not individual ticket details."""

    total_companies = db.scalar(
        select(func.count()).select_from(Tenant)
    ) or 0

    total_users = db.scalar(
        select(func.count())
        .select_from(User)
        .where(
            User.tenant_id.is_not(None),
            User.role.in_([UserRole.admin, UserRole.agent]),
        )
    ) or 0

    total_tickets = db.scalar(
        select(func.count()).select_from(Ticket)
    ) or 0

    status_counts = db.execute(
        select(
            Ticket.status,
            func.count(Ticket.id),
        ).group_by(Ticket.status)
    ).all()

    tickets_by_status = {
        ticket_status.value: 0
        for ticket_status in TicketStatus
    }

    for ticket_status, count in status_counts:
        tickets_by_status[ticket_status.value] = count

    return {
        "total_companies": total_companies,
        "total_users": total_users,
        "total_tickets": total_tickets,
        "open_tickets": tickets_by_status["open"],
        "in_progress_tickets": tickets_by_status["in_progress"],
        "resolved_tickets": tickets_by_status["resolved"],
        "new_tickets": tickets_by_status["new"],
        "pending_agent_tickets": tickets_by_status["pending_agent"],
        "auto_answered_tickets": tickets_by_status["auto_answered"],
        "tickets_by_status": tickets_by_status,
    }


# ==================================================
# TICKETS
# ==================================================

@app.post(
    "/api/v1/tickets",
    response_model=TicketOut,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = require_tenant_user(current_user)

    data = ticket_data.model_dump(
        exclude_unset=True,
        exclude={"tenant_id"},
    )

    ticket = Ticket(**data, tenant_id=tenant_id)

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


@app.post(
    "/api/v1/integrations/aurora/tickets",
    response_model=TicketIntakeOut,
    status_code=status.HTTP_201_CREATED,
)
def create_aurora_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(verify_aurora_integration),
):
    """Save an integration ticket and auto-reply only when customer-safe."""
    # Confirm the configured Aurora Bank tenant exists.
    tenant = db.get(Tenant, tenant_id)

    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Configured Aurora Bank tenant does not exist",
        )

    # 1. Always save the ticket first, so the company sees every ticket.
    ticket = Ticket(
        subject=ticket_data.subject,
        body=ticket_data.body,
        tenant_id=tenant_id,
        status=TicketStatus.new,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    ticket_text = (
        f"Ticket subject: {ticket.subject}\n\n"
        f"Customer issue:\n{ticket.body}"
    )

    try:
        # 2. Search only this company's documents and draft an answer.
        result = answer_question(
            tenant_id=tenant_id,
            query=ticket_text,
            retrieval_query=f"{ticket.subject}\n{ticket.body}",
            company_name=tenant.name,
            verify_evidence=True,
        )

        reply = str(result.get("answer") or "").strip()
        retrieved_sources = result.get("citations")
        has_retrieved_sources = (
            isinstance(retrieved_sources, list)
            and bool(retrieved_sources)
            and all(
                isinstance(source, dict)
                and isinstance(source.get("source"), str)
                and bool(source["source"].strip())
                and source["source"].strip().lower() != "unknown source"
                and bool(source.get("document_id"))
                and bool(source.get("chunk_key"))
                for source in retrieved_sources
            )
        )

        # 3. Collect every reason the ticket needs a human.
        reasons = []

        if result.get("insufficient_evidence"):
            reasons.append("insufficient_evidence")

        if result.get("evidence_check_failed"):
            reasons.append("answer_not_supported_by_evidence")

        if not reply:
            reasons.append("empty_reply")

        if not has_retrieved_sources:
            reasons.append("missing_or_invalid_sources")

        # Only run the safety check when everything else already passed.
        if not reasons and reply_requires_internal_action(
            ticket_text,
            reply,
        ):
            reasons.append("reply_safety_check")

        # 4. Decide: answer the customer, or hand over to an agent.
        if reasons:
            logger.info(
                "Ticket %s routed to an agent: %s; citation_count=%s",
                ticket.id,
                ",".join(reasons),
                (
                    len(retrieved_sources)
                    if isinstance(retrieved_sources, list)
                    else 0
                ),
            )
            ticket.reply = None
            ticket.status = TicketStatus.pending_agent
        else:
            logger.info(
                "Ticket %s received an automatic answer; citation_count=%s",
                ticket.id,
                len(retrieved_sources),
            )
            ticket.reply = reply
            ticket.status = TicketStatus.auto_answered

    except Exception:
        logger.exception(
            "Automatic customer-safe response generation failed for ticket %s",
            ticket.id,
        )
        ticket.reply = None
        ticket.status = TicketStatus.pending_agent

    db.commit()
    db.refresh(ticket)
    return ticket


@app.get(
    "/api/v1/tickets",
    response_model=list[TicketOut],
)
def list_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = require_tenant_user(current_user)

    return db.scalars(
        select(Ticket)
        .where(Ticket.tenant_id == tenant_id)
        .order_by(Ticket.created_at.desc())
    ).all()


@app.get(
    "/api/v1/tickets/{ticket_id}",
    response_model=TicketOut,
)
def get_ticket(
    ticket_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = require_tenant_user(current_user)

    return get_ticket_or_404(db, tenant_id, ticket_id)


@app.patch(
    "/api/v1/tickets/{ticket_id}",
    response_model=TicketOut,
)
def update_ticket(
    ticket_id: uuid.UUID,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = require_tenant_user(current_user)
    ticket = get_ticket_or_404(db, tenant_id, ticket_id)

    updates = ticket_data.model_dump(exclude_unset=True)
    updates.pop("tenant_id", None)

    if updates.get("assigned_to_id") is not None:
        assignee = db.scalar(
            select(User).where(
                User.id == updates["assigned_to_id"],
                User.tenant_id == tenant_id,
            )
        )

        if assignee is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee must belong to your organization",
            )

    for field, value in updates.items():
        setattr(ticket, field, value)

    db.commit()
    db.refresh(ticket)

    return ticket


@app.delete("/api/v1/tickets/{ticket_id}")
def delete_ticket(
    ticket_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company administrators can delete tickets",
        )

    tenant_id = require_tenant_user(current_user)
    ticket = get_ticket_or_404(db, tenant_id, ticket_id)

    try:
        db.delete(ticket)
        db.commit()

        return {
            "message": "Ticket deleted successfully",
            "ticket_id": str(ticket_id),
        }

    except Exception:
        db.rollback()
        logger.exception("Ticket deletion failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete the ticket",
        )


# ==================================================
# AI ANSWERS FOR TICKETS — RAG
# ==================================================

@app.post(
    "/api/v1/tickets/{ticket_id}/ai-answer",
    response_model=AIAnswerOut,
)
def generate_ticket_ai_answer(
    ticket_id: uuid.UUID,
    request: AIAnswerRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = require_tenant_user(current_user)
    ticket = get_ticket_or_404(db, tenant_id, ticket_id)

    tenant = db.get(Tenant, tenant_id)
    company_name = tenant.name if tenant else "the company"

    ticket_context = (
        f"Ticket subject: {ticket.subject}\n\n"
        f"Customer issue:\n{ticket.body}"
    )
    agent_question = (request.question or "").strip() if request else ""
    question = (
        f"{ticket_context}\n\nAgent question:\n{agent_question}"
        if agent_question
        else ticket_context
    )

    try:
        result = answer_question(
            tenant_id=tenant_id,
            query=question,
            retrieval_query=agent_question or ticket_context,
            company_name=company_name,
        )

        return AIAnswerOut(**result)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "RAG answer generation failed for ticket %s",
            ticket_id,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI answer service is temporarily unavailable",
        ) from exc


# ==================================================
# COMPANY DOCUMENTS — SUPABASE STORAGE + QDRANT
# ==================================================

@app.post(
    "/api/v1/documents",
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    tenant_id = require_company_admin(current_user)
    filename = Path(file.filename or "").name.strip()

    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A filename is required",
        )

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOCX, MD and TXT files are supported",
        )

    try:
        content = await file.read(MAX_DOCUMENT_SIZE + 1)

        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is empty",
            )

        if len(content) > MAX_DOCUMENT_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size cannot exceed 10 MB",
            )

        document_id = uuid.uuid4()
        storage_path = f"{tenant_id}/{document_id}{extension}"
        content_type = DOCUMENT_CONTENT_TYPES[extension]

        document = Document(
            id=document_id,
            tenant_id=tenant_id,
            title=Path(filename).stem[:200] or filename[:200],
            filename=filename[:255],
            storage_path=storage_path,
            file_size=len(content),
            uploaded_by_id=current_user.id,
        )

        try:
            supabase.storage.from_(SUPABASE_BUCKET).upload(
                storage_path,
                content,
                file_options={
                    "content-type": content_type,
                    "upsert": "false",
                },
            )
        except Exception as exc:
            logger.exception("Supabase document upload failed")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to store the document",
            ) from exc

        try:
            db.add(document)
            db.commit()
            db.refresh(document)
        except Exception as exc:
            db.rollback()
            logger.exception("Document metadata save failed")

            try:
                remove_storage_object(storage_path)
            except Exception:
                logger.exception(
                    "Could not clean up uploaded object %s",
                    storage_path,
                )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="The document could not be registered",
            ) from exc

        try:
            chunk_count = index_document(
                tenant_id=tenant_id,
                document_id=document.id,
                filename=filename,
                content=content,
            )

            return {
                **document_response(document),
                "rag_indexed": True,
                "chunks_indexed": chunk_count,
            }

        except Exception:
            logger.exception(
                "Document uploaded but RAG indexing failed: %s",
                document.id,
            )

            return {
                **document_response(document),
                "rag_indexed": False,
                "chunks_indexed": 0,
                "indexing_message": (
                    "Document stored successfully, but indexing failed. "
                    "Check the backend logs before retrying."
                ),
            }

    finally:
        await file.close()


@app.get("/api/v1/documents")
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    tenant_id = require_company_admin(current_user)

    documents = db.scalars(
        select(Document)
        .where(Document.tenant_id == tenant_id)
        .order_by(Document.created_at.desc())
    ).all()

    return [document_response(document) for document in documents]


@app.delete("/api/v1/documents/{document_id}")
def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    tenant_id = require_company_admin(current_user)
    document = get_document_or_404(db, tenant_id, document_id)

    storage_path = document.storage_path

    try:
        delete_document_vectors(
            tenant_id=tenant_id,
            document_id=document.id,
        )
    except Exception as exc:
        logger.exception("Qdrant document deletion failed")

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to remove the document from the search index",
        ) from exc

    try:
        remove_storage_object(storage_path)
    except Exception as exc:
        logger.exception("Supabase document deletion failed")

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to delete the stored document",
        ) from exc

    try:
        db.delete(document)
        db.commit()

        return {
            "message": "Document and its search vectors deleted successfully",
            "document_id": str(document_id),
        }

    except Exception as exc:
        db.rollback()
        logger.exception("Document metadata deletion failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "The file and its search vectors were removed, but its "
                "database record could not be deleted. Contact an "
                "administrator."
            ),
        ) from exc


# ==================================================
# AGENT INVITATIONS
# ==================================================

@app.post(
    "/api/v1/invitations",
    status_code=status.HTTP_201_CREATED,
)
def create_invitation(
    invitation_data: InvitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only a tenant administrator can invite agents",
        )

    tenant_id = require_tenant_user(current_user)
    email = str(invitation_data.email).strip().lower()

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    now = datetime.now(timezone.utc)

    active_invitations = db.scalars(
        select(Invitation).where(
            Invitation.tenant_id == tenant_id,
            Invitation.email == email,
            Invitation.accepted_at.is_(None),
        )
    ).all()

    for existing_invitation in active_invitations:
        expiry = existing_invitation.expires_at

        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)

        if expiry > now:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An active invitation already exists for this email",
            )

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()

    invitation = Invitation(
        tenant_id=tenant_id,
        email=email,
        full_name=invitation_data.full_name,
        role=UserRole.agent,
        token_hash=token_hash,
        invited_by_id=current_user.id,
        expires_at=now + timedelta(hours=24),
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    tenant = db.get(Tenant, tenant_id)
    company_name = tenant.name if tenant else "your organization"

    try:
        send_invitation_email(
            recipient_email=email,
            recipient_name=invitation_data.full_name,
            company_name=company_name,
            invitation_token=raw_token,
        )
    except Exception as exc:
        logger.exception(
            "Invitation email delivery failed for invitation %s",
            invitation.id,
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Invitation was created, but the email could not be sent. "
                "Check the backend logs and SMTP configuration."
            ),
        ) from exc

    return {
        "message": "Invitation created and email sent",
        "invitation_id": str(invitation.id),
        "email": email,
        "expires_at": invitation.expires_at,
    }


# ==================================================
# LIST COMPANY INVITATIONS
# ==================================================

@app.get("/api/v1/invitations")
def list_invitations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company administrators can view invitations",
        )

    tenant_id = require_tenant_user(current_user)

    invitations = db.scalars(
        select(Invitation)
        .where(Invitation.tenant_id == tenant_id)
        .order_by(Invitation.created_at.desc())
    ).all()

    now = datetime.now(timezone.utc)
    results = []

    for invitation in invitations:
        expires_at = invitation.expires_at

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if invitation.accepted_at is not None:
            invitation_status = "accepted"
        elif expires_at <= now:
            invitation_status = "expired"
        else:
            invitation_status = "pending"

        results.append({
            "id": str(invitation.id),
            "email": invitation.email,
            "full_name": invitation.full_name,
            "role": invitation.role.value,
            "status": invitation_status,
            "created_at": invitation.created_at,
            "expires_at": invitation.expires_at,
            "accepted_at": invitation.accepted_at,
        })

    return results


@app.delete("/api/v1/invitations/{invitation_id}")
def delete_invitation(
    invitation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company administrators can delete invitations",
        )

    tenant_id = require_tenant_user(current_user)
    invitation = db.scalar(
        select(Invitation).where(
            Invitation.id == invitation_id,
            Invitation.tenant_id == tenant_id,
        )
    )

    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )

    db.delete(invitation)
    db.commit()

    return {"message": "Invitation deleted successfully"}


@app.post("/api/v1/invitations/accept")
def accept_invitation(
    invitation_data: InvitationAccept,
    db: Session = Depends(get_db),
):
    token_hash = hashlib.sha256(
        invitation_data.token.encode("utf-8")
    ).hexdigest()

    invitation = db.scalar(
        select(Invitation).where(
            Invitation.token_hash == token_hash
        )
    )

    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid invitation token",
        )

    now = datetime.now(timezone.utc)
    expiry = invitation.expires_at

    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    if expiry <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired",
        )

    if invitation.accepted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has already been accepted",
        )

    existing_user = db.scalar(
        select(User).where(User.email == invitation.email)
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    try:
        user = User(
            tenant_id=invitation.tenant_id,
            full_name=invitation_data.full_name,
            email=invitation.email,
            password_hash=hash_password(invitation_data.password),
            role=UserRole.agent,
        )

        db.add(user)
        invitation.accepted_at = now

        db.commit()
        db.refresh(user)

        return {
            "message": "Invitation accepted successfully",
            "user_id": str(user.id),
            "email": user.email,
            "role": user.role.value,
        }

    except Exception:
        db.rollback()
        logger.exception("Invitation acceptance failed")
        raise


# ==================================================
# DELETE A COMPANY (PLATFORM ADMIN)
# ==================================================

@app.delete("/api/v1/tenants/{tenant_id}")
def delete_company(
    tenant_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Company not found.",
        )

    # Collect this company's documents so their search vectors can be removed.
    document_ids = db.scalars(
        select(Document.id).where(Document.tenant_id == tenant_id)
    ).all()

    for document_id in document_ids:
        try:
            delete_document_vectors(
                tenant_id=tenant_id,
                document_id=document_id,
            )
        except Exception:
            logger.exception(
                "Could not remove search vectors for document %s",
                document_id,
            )

    try:
        # Delete dependent records before deleting the company.
        db.execute(
            delete(Draft).where(Draft.tenant_id == tenant_id)
        )

        db.execute(
            delete(Invitation).where(Invitation.tenant_id == tenant_id)
        )

        db.execute(
            delete(Document).where(Document.tenant_id == tenant_id)
        )

        db.execute(
            delete(Ticket).where(Ticket.tenant_id == tenant_id)
        )

        db.execute(
            delete(User).where(User.tenant_id == tenant_id)
        )

        db.delete(tenant)
        db.commit()

        return {
            "message": "Company and associated database records deleted successfully.",
            "tenant_id": str(tenant_id),
        }

    except Exception:
        db.rollback()
        logger.exception("Company deletion failed")
        raise HTTPException(
            status_code=500,
            detail="Unable to delete company. Check dependent records and database constraints.",
        )