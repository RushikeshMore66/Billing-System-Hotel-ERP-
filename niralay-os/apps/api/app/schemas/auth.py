"""
Authentication request and response schemas for NiralayOS.

Separates internal data from what's exposed over the wire.
Never expose password_hash or raw refresh tokens in responses.
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------
class LoginRequest(BaseModel):
    """Credentials submitted on POST /auth/login."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=1, description="Plain-text password")

    model_config = {"json_schema_extra": {"examples": [{"email": "admin@niralayos.com", "password": "Admin@NiralayOS2024!"}]}}


class RefreshRequest(BaseModel):
    """Refresh token submitted on POST /auth/refresh."""

    refresh_token: str = Field(..., description="The refresh token issued at login")


class ChangePasswordRequest(BaseModel):
    """Payload for POST /auth/change-password."""

    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=12)
    confirm_password: str = Field(..., min_length=1)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info: object) -> str:
        data = getattr(info, "data", {})
        if "new_password" in data and v != data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class ForgotPasswordRequest(BaseModel):
    """Payload for POST /auth/forgot-password."""

    email: EmailStr = Field(..., description="Account email to send reset link to")


class ResetPasswordRequest(BaseModel):
    """Payload for POST /auth/reset-password."""

    token: str = Field(..., description="Reset token received via email")
    new_password: str = Field(..., min_length=12)
    confirm_password: str = Field(..., min_length=1)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info: object) -> str:
        data = getattr(info, "data", {})
        if "new_password" in data and v != data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------
class TokenResponse(BaseModel):
    """Returned from login and refresh endpoints."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Seconds until access token expiry")


class CurrentUserResponse(BaseModel):
    """Returned from GET /auth/me — never includes sensitive fields."""

    id: int
    uuid: UUID
    username: str
    email: str
    full_name: str
    avatar: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    status: str
    is_superuser: bool
    roles: list[str] = Field(default_factory=list, description="Role names")
    permissions: list[str] = Field(default_factory=list, description="Permission codes")

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    """Simple success/info message returned from action endpoints."""

    message: str
    success: bool = True
