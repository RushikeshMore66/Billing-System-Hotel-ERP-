"""
Restaurant configuration schemas for NiralayOS.

Request/response schemas for:
    RestaurantCategory, MenuCategory, KitchenStation,
    MenuItem, MenuModifier, MenuModifierOption, RestaurantTable
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


# ===========================================================================
# RestaurantCategory
# ===========================================================================
class RestaurantCategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    display_order: int = Field(default=0, ge=0)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)


class RestaurantCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    display_order: Optional[int] = Field(None, ge=0)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class RestaurantCategoryOut(BaseModel):
    id: int
    uuid: UUID
    name: str
    description: Optional[str] = None
    display_order: int
    color: Optional[str] = None
    icon: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# MenuCategory
# ===========================================================================
class MenuCategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    restaurant_category_id: Optional[int] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None
    display_order: int = Field(default=0, ge=0)
    image_url: Optional[str] = Field(None, max_length=512)


class MenuCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    restaurant_category_id: Optional[int] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None
    display_order: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = Field(None, max_length=512)
    is_active: Optional[bool] = None


class MenuCategoryOut(BaseModel):
    id: int
    uuid: UUID
    name: str
    restaurant_category_id: Optional[int] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None
    display_order: int
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# KitchenStation
# ===========================================================================
class KitchenStationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    printer_name: Optional[str] = Field(None, max_length=100)
    display_order: int = Field(default=0, ge=0)


class KitchenStationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    printer_name: Optional[str] = Field(None, max_length=100)
    display_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class KitchenStationOut(BaseModel):
    id: int
    uuid: UUID
    name: str
    description: Optional[str] = None
    printer_name: Optional[str] = None
    display_order: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# MenuModifierOption
# ===========================================================================
class MenuModifierOptionIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price_impact: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    is_default: bool = False
    display_order: int = Field(default=0, ge=0)


class MenuModifierOptionOut(BaseModel):
    id: int
    name: str
    price_impact: Decimal
    is_default: bool
    display_order: int
    is_active: bool

    model_config = {"from_attributes": True}


# ===========================================================================
# MenuModifier
# ===========================================================================
class MenuModifierCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    modifier_type: str = Field(default="single", pattern=r"^(single|multi|quantity)$")
    is_required: bool = False
    min_selections: int = Field(default=0, ge=0)
    max_selections: Optional[int] = Field(None, ge=1)
    display_order: int = Field(default=0, ge=0)
    options: list[MenuModifierOptionIn] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_selections(self) -> "MenuModifierCreate":
        if self.max_selections is not None:
            if self.max_selections < self.min_selections:
                raise ValueError("max_selections must be >= min_selections")
        return self


class MenuModifierUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    modifier_type: Optional[str] = Field(None, pattern=r"^(single|multi|quantity)$")
    is_required: Optional[bool] = None
    min_selections: Optional[int] = Field(None, ge=0)
    max_selections: Optional[int] = Field(None, ge=1)
    display_order: Optional[int] = Field(None, ge=0)
    options: Optional[list[MenuModifierOptionIn]] = None
    is_active: Optional[bool] = None


class MenuModifierOut(BaseModel):
    id: int
    uuid: UUID
    name: str
    description: Optional[str] = None
    modifier_type: str
    is_required: bool
    min_selections: int
    max_selections: Optional[int] = None
    display_order: int
    options: list[MenuModifierOptionOut] = Field(default_factory=list)
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MenuModifierBrief(BaseModel):
    """Lightweight modifier for item listing."""

    id: int
    name: str
    modifier_type: str
    is_required: bool

    model_config = {"from_attributes": True}


# ===========================================================================
# MenuItem
# ===========================================================================
class MenuItemCreate(BaseModel):
    item_code: str = Field(..., min_length=1, max_length=30, pattern=r"^[A-Za-z0-9_-]+$")
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    menu_category_id: Optional[int] = None
    kitchen_station_id: Optional[int] = None
    tax_id: Optional[int] = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    food_type: str = Field(default="veg", pattern=r"^(veg|non_veg|vegan|jain|egg)$")
    is_available: bool = True
    prep_time_minutes: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = Field(None, max_length=512)
    allergens: Optional[str] = Field(None, max_length=255)
    calories: Optional[int] = Field(None, ge=0)
    display_order: int = Field(default=0, ge=0)
    modifier_ids: list[int] = Field(default_factory=list)


class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    menu_category_id: Optional[int] = None
    kitchen_station_id: Optional[int] = None
    tax_id: Optional[int] = None
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    food_type: Optional[str] = Field(None, pattern=r"^(veg|non_veg|vegan|jain|egg)$")
    is_available: Optional[bool] = None
    prep_time_minutes: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = Field(None, max_length=512)
    allergens: Optional[str] = Field(None, max_length=255)
    calories: Optional[int] = Field(None, ge=0)
    display_order: Optional[int] = Field(None, ge=0)
    modifier_ids: Optional[list[int]] = None
    is_active: Optional[bool] = None


class MenuItemOut(BaseModel):
    id: int
    uuid: UUID
    item_code: str
    name: str
    description: Optional[str] = None
    menu_category_id: Optional[int] = None
    kitchen_station_id: Optional[int] = None
    tax_id: Optional[int] = None
    price: Decimal
    cost_price: Optional[Decimal] = None
    food_type: str
    is_available: bool
    prep_time_minutes: Optional[int] = None
    image_url: Optional[str] = None
    allergens: Optional[str] = None
    calories: Optional[int] = None
    display_order: int
    modifiers: list[MenuModifierBrief] = Field(default_factory=list)
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# RestaurantTable
# ===========================================================================
class RestaurantTableCreate(BaseModel):
    table_number: str = Field(..., min_length=1, max_length=20)
    capacity: int = Field(..., ge=1, le=100)
    section: Optional[str] = Field(None, max_length=100)
    location_type: str = Field(default="indoor", pattern=r"^(indoor|outdoor|both)$")
    status: str = Field(default="available", pattern=r"^(available|occupied|reserved|cleaning|blocked)$")
    notes: Optional[str] = None


class RestaurantTableUpdate(BaseModel):
    capacity: Optional[int] = Field(None, ge=1, le=100)
    section: Optional[str] = Field(None, max_length=100)
    location_type: Optional[str] = Field(None, pattern=r"^(indoor|outdoor|both)$")
    status: Optional[str] = Field(None, pattern=r"^(available|occupied|reserved|cleaning|blocked)$")
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class RestaurantTableOut(BaseModel):
    id: int
    uuid: UUID
    table_number: str
    capacity: int
    section: Optional[str] = None
    location_type: str
    status: str
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
