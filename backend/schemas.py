import uuid
import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator
from sqlalchemy import select, func

from models import TicketStatus

def validate_password_rules(password: str) -> str:
    if not 12 <= len(password) <= 128:
        raise ValueError("Password must be between 12 and 128 characters.")

    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter.")

    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter.")

    if not re.search(r"[0-9]", password):
        raise ValueError("Password must contain at least one number.")

    if not re.search(r"[^A-Za-z0-9\s]", password):
        raise ValueError("Password must contain at least one special character.")

    if re.search(r"\s", password):
        raise ValueError("Password must not contain spaces.")

    return password

class TicketCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    body: str = Field(min_length=1)


class TicketUpdate(BaseModel):
    subject: Optional[str] = Field(default=None, min_length=3, max_length=200)
    body: Optional[str] = Field(default=None, min_length=1)
    status: Optional[TicketStatus] = None


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    subject: str
    body: str
    status: TicketStatus
    reply: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TicketIntakeOut(TicketOut):
    pass


class TenantOut(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    owner_email: str | None = None

    model_config = ConfigDict(from_attributes=True)

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    tenant_id: uuid.UUID
    role: str = "agent"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    role: str

class OrganizationRegister(BaseModel):
    company_name: str = Field(min_length=2, max_length=120)
    admin_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

    @field_validator("password")
    @classmethod
    def check_password(cls, password: str) -> str:
        return validate_password_rules(password)

class InvitationCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)


class InvitationAccept(BaseModel):
    token: str
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=12, max_length=128)

    @field_validator("password")
    @classmethod
    def check_password(cls, password: str) -> str:
        return validate_password_rules(password)

class AIAnswerOut(BaseModel):
    answer: str
    insufficient_evidence: bool
    citations: list[dict] = Field(default_factory=list)


class AIAnswerRequest(BaseModel):
    question: Optional[str] = Field(default=None, max_length=2000)