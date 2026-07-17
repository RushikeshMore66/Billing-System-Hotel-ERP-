"""
Role and Permission schemas for NiralayOS.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Permission schemas
# ---------------------------------------------------------------------------
class PermissionCreate(BaseModel):
    code: str = Field(..., pattern=r"^[a-z_]+:[a-z_]+$", description="module:action format")
    module: str = Field(..., min_length=1, max_length=80)
    action: str = Field(..., min_length=1, max_length=80)
    description: Optional[str] = None


class PermissionOut(BaseModel):
    id: int
    uuid: UUID
    code: str
    module: str
    action: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Role schemas
# ---------------------------------------------------------------------------
class RoleCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-z0-9_-]+$")
    description: Optional[str] = None
    permission_ids: list[int] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "examples": [{"name": "Night Auditor", "slug": "night_auditor", "permission_ids": [1, 5, 12]}]
        }
    }


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    permission_ids: Optional[list[int]] = None


class RoleOut(BaseModel):
    id: int
    uuid: UUID
    name: str
    slug: str
    description: Optional[str] = None
    is_system: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RoleWithPermissions(RoleOut):
    permissions: list[PermissionOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Assignment schemas
# ---------------------------------------------------------------------------
class AssignPermissionsRequest(BaseModel):
    permission_ids: list[int] = Field(..., min_length=1)


class AssignRoleRequest(BaseModel):
    role_id: int
