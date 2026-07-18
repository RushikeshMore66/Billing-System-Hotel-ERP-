"""
Property configuration schemas for NiralayOS.

Request (Create/Update) and response (Out) schemas for:
    PropertyProfile, Floor, Amenity, BedType, RoomType, Room,
    Tax, PaymentMethod, Currency, Season, RatePlan
"""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


# ===========================================================================
# PropertyProfile
# ===========================================================================
class PropertyProfileUpdate(BaseModel):
    """PATCH /property/profile — all fields optional."""

    hotel_name: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=512)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=320)
    phone: Optional[str] = Field(None, max_length=30)
    website: Optional[str] = Field(None, max_length=512)
    gst_number: Optional[str] = Field(None, max_length=15)
    pan_number: Optional[str] = Field(None, max_length=10)
    currency_code: Optional[str] = Field(None, min_length=3, max_length=3)
    timezone: Optional[str] = Field(None, max_length=60)
    language: Optional[str] = Field(None, max_length=10)
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    invoice_prefix: Optional[str] = Field(None, max_length=10)
    business_registration_number: Optional[str] = Field(None, max_length=100)
    business_registration_details: Optional[str] = None
    star_rating: Optional[int] = Field(None, ge=1, le=5)

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "hotel_name": "The Grand Niralay",
                "email": "info@grandniralay.com",
                "gst_number": "27AAPCS1751H1ZN",
                "check_in_time": "14:00:00",
                "check_out_time": "11:00:00",
            }]
        }
    }


class PropertyProfileOut(BaseModel):
    id: int
    uuid: UUID
    hotel_name: str
    logo_url: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    currency_code: str
    timezone: str
    language: str
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    invoice_prefix: str
    business_registration_number: Optional[str] = None
    business_registration_details: Optional[str] = None
    star_rating: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# Floor
# ===========================================================================
class FloorCreate(BaseModel):
    floor_number: int
    floor_name: str = Field(..., min_length=1, max_length=100)
    display_order: int = Field(default=0, ge=0)
    status: str = Field(default="active", pattern=r"^(active|inactive)$")


class FloorUpdate(BaseModel):
    floor_number: Optional[int] = None
    floor_name: Optional[str] = Field(None, min_length=1, max_length=100)
    display_order: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern=r"^(active|inactive)$")


class FloorOut(BaseModel):
    id: int
    uuid: UUID
    floor_number: int
    floor_name: str
    display_order: int
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# Amenity
# ===========================================================================
class AmenityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None


class AmenityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AmenityOut(BaseModel):
    id: int
    uuid: UUID
    name: str
    icon: Optional[str] = None
    description: Optional[str] = None
    is_system: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# BedType
# ===========================================================================
class BedTypeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class BedTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class BedTypeOut(BaseModel):
    id: int
    uuid: UUID
    name: str
    description: Optional[str] = None
    is_system: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# RoomTypeImage
# ===========================================================================
class RoomTypeImageIn(BaseModel):
    image_url: str = Field(..., max_length=512)
    caption: Optional[str] = Field(None, max_length=255)
    display_order: int = Field(default=0, ge=0)


class RoomTypeImageOut(BaseModel):
    id: int
    image_url: str
    caption: Optional[str] = None
    display_order: int

    model_config = {"from_attributes": True}


# ===========================================================================
# RoomType
# ===========================================================================
class RoomTypeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    base_price: Decimal = Field(..., gt=0, decimal_places=2)
    weekend_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    max_occupancy: int = Field(default=2, ge=1, le=20)
    extra_bed_allowed: bool = False
    extra_bed_charge: Optional[Decimal] = Field(None, ge=0)
    status: str = Field(default="active", pattern=r"^(active|inactive)$")
    amenity_ids: list[int] = Field(default_factory=list)
    images: list[RoomTypeImageIn] = Field(default_factory=list)


class RoomTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    base_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    weekend_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    max_occupancy: Optional[int] = Field(None, ge=1, le=20)
    extra_bed_allowed: Optional[bool] = None
    extra_bed_charge: Optional[Decimal] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern=r"^(active|inactive)$")
    amenity_ids: Optional[list[int]] = None
    images: Optional[list[RoomTypeImageIn]] = None


class RoomTypeOut(BaseModel):
    id: int
    uuid: UUID
    name: str
    description: Optional[str] = None
    base_price: Decimal
    weekend_price: Optional[Decimal] = None
    max_occupancy: int
    extra_bed_allowed: bool
    extra_bed_charge: Optional[Decimal] = None
    status: str
    amenities: list[AmenityOut] = Field(default_factory=list)
    images: list[RoomTypeImageOut] = Field(default_factory=list)
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RoomTypeBrief(BaseModel):
    """Lightweight room type for nested display."""

    id: int
    uuid: UUID
    name: str
    base_price: Decimal

    model_config = {"from_attributes": True}


# ===========================================================================
# Room
# ===========================================================================
class RoomCreate(BaseModel):
    room_number: str = Field(..., min_length=1, max_length=20)
    floor_id: Optional[int] = None
    room_type_id: int
    capacity: int = Field(default=2, ge=1)
    view: Optional[str] = Field(None, max_length=100)
    status: str = Field(
        default="available",
        pattern=r"^(available|occupied|out_of_order)$",
    )
    housekeeping_status: str = Field(
        default="clean",
        pattern=r"^(clean|dirty|inspected|out_of_service)$",
    )
    maintenance_status: str = Field(
        default="operational",
        pattern=r"^(operational|under_maintenance|out_of_order)$",
    )
    notes: Optional[str] = None


class RoomUpdate(BaseModel):
    floor_id: Optional[int] = None
    room_type_id: Optional[int] = None
    capacity: Optional[int] = Field(None, ge=1)
    view: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(
        None,
        pattern=r"^(available|occupied|out_of_order)$",
    )
    housekeeping_status: Optional[str] = Field(
        None,
        pattern=r"^(clean|dirty|inspected|out_of_service)$",
    )
    maintenance_status: Optional[str] = Field(
        None,
        pattern=r"^(operational|under_maintenance|out_of_order)$",
    )
    notes: Optional[str] = None


class RoomOut(BaseModel):
    id: int
    uuid: UUID
    room_number: str
    floor_id: Optional[int] = None
    room_type_id: int
    room_type: Optional[RoomTypeBrief] = None
    capacity: int
    view: Optional[str] = None
    status: str
    housekeeping_status: str
    maintenance_status: str
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RoomBulkCreate(BaseModel):
    rooms: list[RoomCreate] = Field(..., min_length=1, max_length=500)


class RoomBulkResult(BaseModel):
    created: int
    failed: int
    errors: list[dict[str, str]] = Field(default_factory=list)


# ===========================================================================
# Tax
# ===========================================================================
class TaxCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=30, pattern=r"^[A-Z0-9_]+$")
    tax_type: str = Field(default="percentage", pattern=r"^(percentage|fixed)$")
    rate: Decimal = Field(..., ge=0, decimal_places=4)
    is_inclusive: bool = False
    applies_to: str = Field(default="all", pattern=r"^(all|rooms|restaurant|services)$")
    description: Optional[str] = None

    @field_validator("rate")
    @classmethod
    def validate_rate(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("Tax rate cannot be negative")
        return v


class TaxUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    tax_type: Optional[str] = Field(None, pattern=r"^(percentage|fixed)$")
    rate: Optional[Decimal] = Field(None, ge=0)
    is_inclusive: Optional[bool] = None
    applies_to: Optional[str] = Field(None, pattern=r"^(all|rooms|restaurant|services)$")
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TaxOut(BaseModel):
    id: int
    uuid: UUID
    name: str
    code: str
    tax_type: str
    rate: Decimal
    is_inclusive: bool
    applies_to: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# PaymentMethod
# ===========================================================================
class PaymentMethodCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=30, pattern=r"^[a-z0-9_]+$")
    payment_type: str = Field(
        ...,
        pattern=r"^(cash|upi|credit_card|debit_card|net_banking|wallet|bank_transfer|other)$",
    )
    requires_reference: bool = False
    icon: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None


class PaymentMethodUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    payment_type: Optional[str] = Field(
        None,
        pattern=r"^(cash|upi|credit_card|debit_card|net_banking|wallet|bank_transfer|other)$",
    )
    requires_reference: Optional[bool] = None
    icon: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PaymentMethodOut(BaseModel):
    id: int
    uuid: UUID
    name: str
    code: str
    payment_type: str
    is_system: bool
    requires_reference: bool
    icon: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# Currency
# ===========================================================================
class CurrencyCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    name: str = Field(..., min_length=1, max_length=100)
    symbol: str = Field(..., min_length=1, max_length=5)
    exchange_rate: Decimal = Field(default=Decimal("1.0"), gt=0)
    decimal_places: int = Field(default=2, ge=0, le=4)
    is_default: bool = False


class CurrencyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    symbol: Optional[str] = Field(None, min_length=1, max_length=5)
    exchange_rate: Optional[Decimal] = Field(None, gt=0)
    decimal_places: Optional[int] = Field(None, ge=0, le=4)
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class CurrencyOut(BaseModel):
    id: int
    uuid: UUID
    code: str
    name: str
    symbol: str
    exchange_rate: Decimal
    decimal_places: int
    is_default: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# Season
# ===========================================================================
class SeasonCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    start_date: date
    end_date: date
    priority: int = Field(default=0, ge=0)
    description: Optional[str] = None

    @model_validator(mode="after")
    def validate_dates(self) -> "SeasonCreate":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class SeasonUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    priority: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    is_active: Optional[bool] = None

    @model_validator(mode="after")
    def validate_dates(self) -> "SeasonUpdate":
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date must be on or after start_date")
        return self


class SeasonOut(BaseModel):
    id: int
    uuid: UUID
    name: str
    start_date: date
    end_date: date
    priority: int
    description: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# RatePlanSeasonRate
# ===========================================================================
class RatePlanSeasonRateIn(BaseModel):
    room_type_id: int
    season_id: Optional[int] = None
    price_per_night: Decimal = Field(..., gt=0, decimal_places=2)
    weekend_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    extra_person_charge: Optional[Decimal] = Field(None, ge=0)


class RatePlanSeasonRateOut(BaseModel):
    id: int
    room_type_id: int
    season_id: Optional[int] = None
    price_per_night: Decimal
    weekend_price: Optional[Decimal] = None
    extra_person_charge: Optional[Decimal] = None

    model_config = {"from_attributes": True}


# ===========================================================================
# RatePlan
# ===========================================================================
class RatePlanCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=30, pattern=r"^[A-Z0-9_]+$")
    description: Optional[str] = None
    meal_plan: str = Field(default="EP", pattern=r"^(EP|CP|MAP|AP)$")
    is_default: bool = False
    min_stay_nights: int = Field(default=1, ge=1)
    max_stay_nights: Optional[int] = Field(None, ge=1)
    cancellation_policy: Optional[str] = None
    season_rates: list[RatePlanSeasonRateIn] = Field(default_factory=list)


class RatePlanUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    meal_plan: Optional[str] = Field(None, pattern=r"^(EP|CP|MAP|AP)$")
    is_default: Optional[bool] = None
    min_stay_nights: Optional[int] = Field(None, ge=1)
    max_stay_nights: Optional[int] = Field(None, ge=1)
    cancellation_policy: Optional[str] = None
    season_rates: Optional[list[RatePlanSeasonRateIn]] = None
    is_active: Optional[bool] = None


class RatePlanOut(BaseModel):
    id: int
    uuid: UUID
    name: str
    code: str
    description: Optional[str] = None
    meal_plan: str
    is_default: bool
    min_stay_nights: int
    max_stay_nights: Optional[int] = None
    cancellation_policy: Optional[str] = None
    season_rates: list[RatePlanSeasonRateOut] = Field(default_factory=list)
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
