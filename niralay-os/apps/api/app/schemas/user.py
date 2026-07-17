"""
User request/response schemas for NiralayOS.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

import re

_PASSWORD_RE = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{12,}$"
)


def _validate_password_strength(v: str) -> str:
    if not _PASSWORD_RE.match(v):
        raise ValueError(
            "Password must be at least 12 characters and contain uppercase, "
            "lowercase, digit, and special character."
        )
    return v


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------
class UserCreate(BaseModel):
    """Payload for POST /users."""

    username: str = Field(..., min_length=3, max_length=150, pattern=r"^[a-zA-Z0-9_.-]+$")
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    password: str = Field(..., min_length=12)
    full_name: str = Field(..., min_length=1, max_length=255)
    department: Optional[str] = Field(None, max_length=150)
    designation: Optional[str] = Field(None, max_length=150)
    is_superuser: bool = False
    role_ids: list[int] = Field(default_factory=list)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password_strength(v)

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "username": "john.doe",
                "email": "john@niralayos.com",
                "password": "Secure@Pass123!",
                "full_name": "John Doe",
                "role_ids": [2],
            }]
        }
    }


class UserUpdate(BaseModel):
    """Payload for PATCH /users/{id} — all fields optional."""

    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    avatar: Optional[str] = Field(None, max_length=512)
    department: Optional[str] = Field(None, max_length=150)
    designation: Optional[str] = Field(None, max_length=150)
    status: Optional[str] = Field(None, pattern=r"^(active|inactive|suspended)$")
    role_ids: Optional[list[int]] = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------
class RoleInUser(BaseModel):
    id: int
    name: str
    slug: str

    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    """Safe user representation — never exposes password_hash."""

    id: int
    uuid: UUID
    username: str
    email: str
    phone: Optional[str] = None
    full_name: str
    avatar: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    status: str
    is_superuser: bool
    is_active: bool
    roles: list[RoleInUser] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListOut(BaseModel):
    """Lightweight user representation for list endpoints."""

    id: int
    uuid: UUID
    username: str
    email: str
    full_name: str
    status: str
    is_superuser: bool
    is_active: bool
    roles: list[RoleInUser] = Field(default_factory=list)
    created_at: datetime

    model_config = {"from_attributes": True}
