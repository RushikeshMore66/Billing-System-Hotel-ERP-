"""
Inventory schemas for NiralayOS.

Request/response schemas for:
    InventoryCategory, StoreLocation, InventoryItem, StockMovement
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# InventoryCategory
# ---------------------------------------------------------------------------
class InventoryCategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    display_order: int = 0
    color: Optional[str] = None
    icon: Optional[str] = None

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not (v.startswith("#") and len(v) in (4, 7)):
            raise ValueError("color must be a valid hex color code (e.g. #155E4B)")
        return v


class InventoryCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    display_order: Optional[int] = None
    color: Optional[str] = None
    icon: Optional[str] = None

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not (v.startswith("#") and len(v) in (4, 7)):
            raise ValueError("color must be a valid hex color code")
        return v


class InventoryCategoryOut(BaseModel):
    id: int
    uuid: UUID
    name: str
    description: Optional[str] = None
    display_order: int
    color: Optional[str] = None
    icon: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# StoreLocation
# ---------------------------------------------------------------------------
class StoreLocationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=30)
    description: Optional[str] = None
    display_order: int = 0


class StoreLocationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    display_order: Optional[int] = None


class StoreLocationOut(BaseModel):
    id: int
    uuid: UUID
    name: str
    code: str
    description: Optional[str] = None
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# InventoryItem
# ---------------------------------------------------------------------------
class InventoryCategoryBrief(BaseModel):
    id: int
    name: str
    color: Optional[str] = None
    icon: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StoreLocationBrief(BaseModel):
    id: int
    name: str
    code: str

    model_config = ConfigDict(from_attributes=True)


class InventoryItemCreate(BaseModel):
    sku: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category_id: Optional[int] = None
    location_id: Optional[int] = None
    unit: str = Field(default="piece", max_length=30)
    item_type: str = Field(default="consumable")
    current_stock: Decimal = Field(default=Decimal("0"), ge=0)
    minimum_stock: Decimal = Field(default=Decimal("0"), ge=0)
    reorder_level: Optional[Decimal] = Field(None, ge=0)
    maximum_stock: Optional[Decimal] = Field(None, ge=0)
    purchase_price: Optional[Decimal] = Field(None, ge=0)
    supplier_name: Optional[str] = None
    supplier_contact: Optional[str] = None
    has_expiry: bool = False
    expiry_date: Optional[date] = None
    batch_number: Optional[str] = None
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    notes: Optional[str] = None
    image_url: Optional[str] = None

    @field_validator("item_type")
    @classmethod
    def validate_item_type(cls, v: str) -> str:
        valid = {"consumable", "reusable", "asset"}
        if v not in valid:
            raise ValueError(f"item_type must be one of: {', '.join(sorted(valid))}")
        return v


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category_id: Optional[int] = None
    location_id: Optional[int] = None
    unit: Optional[str] = None
    item_type: Optional[str] = None
    minimum_stock: Optional[Decimal] = Field(None, ge=0)
    reorder_level: Optional[Decimal] = Field(None, ge=0)
    maximum_stock: Optional[Decimal] = Field(None, ge=0)
    purchase_price: Optional[Decimal] = Field(None, ge=0)
    supplier_name: Optional[str] = None
    supplier_contact: Optional[str] = None
    has_expiry: Optional[bool] = None
    expiry_date: Optional[date] = None
    batch_number: Optional[str] = None
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    notes: Optional[str] = None
    image_url: Optional[str] = None


class InventoryItemOut(BaseModel):
    id: int
    uuid: UUID
    sku: str
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    category: Optional[InventoryCategoryBrief] = None
    location_id: Optional[int] = None
    location: Optional[StoreLocationBrief] = None
    unit: str
    item_type: str
    current_stock: Decimal
    minimum_stock: Decimal
    reorder_level: Optional[Decimal] = None
    maximum_stock: Optional[Decimal] = None
    purchase_price: Optional[Decimal] = None
    supplier_name: Optional[str] = None
    supplier_contact: Optional[str] = None
    has_expiry: bool
    expiry_date: Optional[date] = None
    batch_number: Optional[str] = None
    tax_rate: Optional[Decimal] = None
    notes: Optional[str] = None
    image_url: Optional[str] = None
    stock_level: str = Field(..., description="ok | low | critical")
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# StockMovement
# ---------------------------------------------------------------------------
class StockMovementCreate(BaseModel):
    item_id: int
    movement_type: str
    quantity: Decimal = Field(..., gt=0)
    unit_cost: Optional[Decimal] = Field(None, ge=0)
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    supplier_name: Optional[str] = None
    from_location_id: Optional[int] = None
    to_location_id: Optional[int] = None
    movement_date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("movement_type")
    @classmethod
    def validate_movement_type(cls, v: str) -> str:
        valid = {
            "opening", "purchase", "return_in", "consumption",
            "damage", "loss", "adjustment", "transfer_in", "transfer_out",
        }
        if v not in valid:
            raise ValueError(f"movement_type must be one of: {', '.join(sorted(valid))}")
        return v


class StockMovementOut(BaseModel):
    id: int
    item_id: int
    movement_type: str
    quantity: Decimal
    stock_before: Decimal
    stock_after: Decimal
    unit_cost: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    supplier_name: Optional[str] = None
    from_location_id: Optional[int] = None
    to_location_id: Optional[int] = None
    notes: Optional[str] = None
    movement_date: date
    recorded_by: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Stock level summary
# ---------------------------------------------------------------------------
class StockLevelSummary(BaseModel):
    total_items: int
    ok_count: int
    low_count: int
    critical_count: int
    out_of_stock_count: int
