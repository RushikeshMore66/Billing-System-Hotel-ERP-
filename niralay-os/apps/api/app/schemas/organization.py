"""
Organisation configuration schemas for NiralayOS.

Request/response schemas for:
    Department, Designation, GuestIDType
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ===========================================================================
# Department
# ===========================================================================
class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=30, pattern=r"^[A-Z0-9_]+$")
    description: Optional[str] = None
    display_order: int = Field(default=0, ge=0)


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    display_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class DepartmentOut(BaseModel):
    id: int
    uuid: UUID
    name: str
    code: str
    description: Optional[str] = None
    is_system: bool
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# Designation
# ===========================================================================
class DesignationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=30, pattern=r"^[A-Z0-9_]+$")
    department_id: Optional[int] = None
    description: Optional[str] = None
    display_order: int = Field(default=0, ge=0)


class DesignationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    department_id: Optional[int] = None
    description: Optional[str] = None
    display_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class DesignationOut(BaseModel):
    id: int
    uuid: UUID
    name: str
    code: str
    department_id: Optional[int] = None
    description: Optional[str] = None
    is_system: bool
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# GuestIDType
# ===========================================================================
class GuestIDTypeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=30, pattern=r"^[A-Z0-9_]+$")
    description: Optional[str] = None
    requires_expiry: bool = False
    display_order: int = Field(default=0, ge=0)


class GuestIDTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    requires_expiry: Optional[bool] = None
    display_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class GuestIDTypeOut(BaseModel):
    id: int
    uuid: UUID
    name: str
    code: str
    description: Optional[str] = None
    is_system: bool
    requires_expiry: bool
    display_order: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
