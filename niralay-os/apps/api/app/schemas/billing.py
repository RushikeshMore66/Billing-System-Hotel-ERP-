"""
Billing schemas for NiralayOS.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# BillItem
# ---------------------------------------------------------------------------
class BillItemCreate(BaseModel):
    item_type: str = Field(default="service")
    description: str = Field(..., min_length=1, max_length=500)
    menu_item_id: Optional[int] = None
    quantity: Decimal = Field(default=Decimal("1"), gt=0)
    unit_price: Decimal = Field(..., ge=0)
    discount_pct: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    display_order: int = 0
    notes: Optional[str] = None


class BillItemOut(BaseModel):
    id: int
    bill_id: int
    item_type: str
    description: str
    menu_item_id: Optional[int] = None
    quantity: Decimal
    unit_price: Decimal
    discount_pct: Decimal
    tax_rate: Decimal
    amount: Decimal
    tax_amount: Decimal
    total: Decimal
    display_order: int
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------
class PaymentCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    payment_method_id: Optional[int] = None
    payment_type: Optional[str] = None
    payment_date: Optional[date] = None
    reference_number: Optional[str] = None
    transaction_id: Optional[str] = None
    notes: Optional[str] = None


class PaymentOut(BaseModel):
    id: int
    uuid: UUID
    bill_id: int
    payment_method_id: Optional[int] = None
    amount: Decimal
    payment_date: date
    status: str
    reference_number: Optional[str] = None
    transaction_id: Optional[str] = None
    payment_type: Optional[str] = None
    notes: Optional[str] = None
    is_refund: bool
    original_payment_id: Optional[int] = None
    received_by: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Bill
# ---------------------------------------------------------------------------
class BillCreate(BaseModel):
    reservation_id: Optional[int] = None
    guest_id: Optional[int] = None
    table_number: Optional[str] = None
    bill_type: str = Field(default="room")
    bill_date: Optional[date] = None
    items: list[BillItemCreate] = Field(default_factory=list)
    notes: Optional[str] = None
    gst_number: Optional[str] = None

    @field_validator("bill_type")
    @classmethod
    def validate_bill_type(cls, v: str) -> str:
        valid = {"room", "restaurant", "mixed", "other"}
        if v not in valid:
            raise ValueError(f"bill_type must be one of: {', '.join(sorted(valid))}")
        return v

    @field_validator("items")
    @classmethod
    def validate_items_not_empty(cls, v: list) -> list:
        if len(v) == 0:
            raise ValueError("A bill must have at least one line item")
        return v



class BillUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    void_reason: Optional[str] = None
    gst_number: Optional[str] = None


class BillOut(BaseModel):
    id: int
    uuid: UUID
    bill_number: str
    bill_date: date
    bill_type: str
    reservation_id: Optional[int] = None
    guest_id: Optional[int] = None
    table_number: Optional[str] = None
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    amount_due: Decimal
    status: str
    notes: Optional[str] = None
    gst_number: Optional[str] = None
    void_reason: Optional[str] = None
    items: list[BillItemOut] = Field(default_factory=list)
    payments: list[PaymentOut] = Field(default_factory=list)
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BillSummary(BaseModel):
    """Lightweight bill record for lists (no items/payments)."""
    id: int
    uuid: UUID
    bill_number: str
    bill_date: date
    bill_type: str
    reservation_id: Optional[int] = None
    guest_id: Optional[int] = None
    table_number: Optional[str] = None
    total_amount: Decimal
    amount_paid: Decimal
    amount_due: Decimal
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
