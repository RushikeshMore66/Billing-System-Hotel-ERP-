"""
Session and AuditLog response schemas for NiralayOS.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class SessionOut(BaseModel):
    """Active session summary returned to the user."""

    id: int
    uuid: UUID
    ip_address: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    login_at: datetime
    last_activity_at: Optional[datetime] = None
    expires_at: datetime
    is_revoked: bool

    model_config = {"from_attributes": True}


class AuditLogOut(BaseModel):
    """Single audit log entry for admin review."""

    id: int
    actor_uuid: Optional[str] = None
    event: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    outcome: str
    detail: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
