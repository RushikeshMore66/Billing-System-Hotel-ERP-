"""
Schemas for Reservation.
"""
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.core.constants import ReservationStatus, ReservationSource
from app.schemas.guest import GuestResponse

class ReservationBase(BaseModel):
    room_id: Optional[int] = None
    room_type_id: int
    check_in_date: date
    check_out_date: date
    nights: int = Field(1, ge=1)
    adults: int = Field(1, ge=1)
    children: int = Field(0, ge=0)
    source: ReservationSource = ReservationSource.DIRECT
    rate_plan_id: Optional[int] = None
    base_amount: float = Field(0.0, ge=0)
    tax_amount: float = Field(0.0, ge=0)
    total_amount: float = Field(0.0, ge=0)
    advance_paid: float = Field(0.0, ge=0)
    special_requests: Optional[str] = None
    notes: Optional[str] = None

class ReservationCreate(ReservationBase):
    guest_id: int

class ReservationUpdate(BaseModel):
    room_id: Optional[int] = None
    room_type_id: Optional[int] = None
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    nights: Optional[int] = Field(None, ge=1)
    adults: Optional[int] = Field(None, ge=1)
    children: Optional[int] = Field(None, ge=0)
    source: Optional[ReservationSource] = None
    rate_plan_id: Optional[int] = None
    base_amount: Optional[float] = Field(None, ge=0)
    tax_amount: Optional[float] = Field(None, ge=0)
    total_amount: Optional[float] = Field(None, ge=0)
    advance_paid: Optional[float] = Field(None, ge=0)
    special_requests: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[ReservationStatus] = None

class ReservationStatusHistoryResponse(BaseModel):
    id: int
    from_status: Optional[str] = None
    to_status: str
    changed_by: Optional[str] = None
    changed_at: datetime
    remarks: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ReservationResponse(ReservationBase):
    id: int
    uuid: UUID
    reservation_number: str
    guest_id: int
    status: ReservationStatus
    guest: Optional[GuestResponse] = None
    is_active: bool
    created_at: str

    model_config = ConfigDict(from_attributes=True)
