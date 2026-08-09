"""
Expense schemas for NiralayOS.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# ExpenseCategory
# ---------------------------------------------------------------------------
class ExpenseCategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    display_order: int = 0


class ExpenseCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    display_order: Optional[int] = None


class ExpenseCategoryOut(BaseModel):
    id: int
    uuid: UUID
    name: str
    description: Optional[str] = None
    display_order: int
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Expense
# ---------------------------------------------------------------------------
class ExpenseCategoryBrief(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ExpenseCreate(BaseModel):
    category_id: Optional[int] = None
    description: str = Field(..., min_length=1, max_length=500)
    amount: Decimal = Field(..., gt=0)
    tax_amount: Decimal = Field(default=Decimal("0"), ge=0)
    expense_date: date
    payment_method: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_contact: Optional[str] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class ExpenseUpdate(BaseModel):
    category_id: Optional[int] = None
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    amount: Optional[Decimal] = Field(None, gt=0)
    tax_amount: Optional[Decimal] = Field(None, ge=0)
    expense_date: Optional[date] = None
    payment_method: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_contact: Optional[str] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class ExpenseOut(BaseModel):
    id: int
    uuid: UUID
    category_id: Optional[int] = None
    category: Optional[ExpenseCategoryBrief] = None
    description: str
    amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    expense_date: date
    payment_method: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_contact: Optional[str] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Expense summary
# ---------------------------------------------------------------------------
class ExpenseSummary(BaseModel):
    total_expenses: Decimal
    total_tax: Decimal
    grand_total: Decimal
    count: int
    by_category: list[dict]
