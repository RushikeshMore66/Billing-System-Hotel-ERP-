"""
Schemas for Guest.
"""
from datetime import date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class GuestBase(BaseModel):
    full_name: str = Field(..., max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    id_type_id: Optional[int] = None
    id_number: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = Field("Indian", max_length=100)
    address: Optional[str] = None
    notes: Optional[str] = None

class GuestCreate(GuestBase):
    pass

class GuestUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    id_type_id: Optional[int] = None
    id_number: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None
    notes: Optional[str] = None

class GuestResponse(GuestBase):
    id: int
    uuid: UUID
    is_active: bool
    created_at: str

    model_config = ConfigDict(from_attributes=True)
