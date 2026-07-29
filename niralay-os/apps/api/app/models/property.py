"""
Property configuration models for NiralayOS.

Covers the complete hotel property setup:
    PropertyProfile, Floor, Amenity, BedType,
    RoomType, Room, Tax, PaymentMethod, Currency,
    Season, RatePlan, RatePlanSeasonRate

All models inherit AuditMixin which provides:
    id, uuid, created_at, updated_at, created_by, updated_by,
    deleted_at, is_active  (soft-delete support)
"""

from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base

if TYPE_CHECKING:
    from app.models.restaurant import MenuItem
    from app.models.organization import Department


# ---------------------------------------------------------------------------
# Association table: room_types ↔ amenities  (many-to-many)
# ---------------------------------------------------------------------------
room_type_amenities = Table(
    "room_type_amenities",
    Base.metadata,
    Column(
        "room_type_id",
        Integer,
        ForeignKey("room_types.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "amenity_id",
        Integer,
        ForeignKey("amenities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "added_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
)


# ---------------------------------------------------------------------------
# PropertyProfile  (singleton — one row per deployment)
# ---------------------------------------------------------------------------
class PropertyProfile(AuditMixin, Base):
    """
    Core hotel identity and configuration.

    There is exactly one row in this table.
    Use PropertyProfileRepository.get_or_create() to retrieve/initialise it.
    """

    __tablename__ = "property_profiles"

    hotel_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="My Hotel",
        comment="Hotel display name",
    )
    logo_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="Public URL or relative path to hotel logo",
    )
    address_line1: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default="India")
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    gst_number: Mapped[Optional[str]] = mapped_column(
        String(15),
        nullable=True,
        comment="15-digit GST registration number",
    )
    pan_number: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        comment="10-character PAN number",
    )
    currency_code: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="INR",
        comment="ISO 4217 currency code",
    )
    timezone: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
        default="Asia/Kolkata",
    )
    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="en",
    )
    check_in_time: Mapped[Optional[time]] = mapped_column(
        Time(),
        nullable=True,
        comment="Default check-in time (local)",
    )
    check_out_time: Mapped[Optional[time]] = mapped_column(
        Time(),
        nullable=True,
        comment="Default check-out time (local)",
    )
    invoice_prefix: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="INV",
        comment="Prefix for generated invoice numbers",
    )
    business_registration_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    business_registration_details: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    star_rating: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Hotel star rating 1-5",
    )


# ---------------------------------------------------------------------------
# Floor
# ---------------------------------------------------------------------------
class Floor(AuditMixin, Base):
    """Hotel floor / level configuration."""

    __tablename__ = "floors"

    floor_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Numeric floor identifier (can be negative for basements)",
    )
    floor_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Human-readable name, e.g. 'Ground Floor'",
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        comment="active | inactive",
    )

    # Relationships
    rooms: Mapped[list["Room"]] = relationship(
        "Room",
        back_populates="floor",
        lazy="dynamic",
    )

    __table_args__ = (
        UniqueConstraint("floor_number", name="uq_floors_floor_number"),
        Index("ix_floors_status", "status"),
        Index("ix_floors_display_order", "display_order"),
    )


# ---------------------------------------------------------------------------
# Amenity
# ---------------------------------------------------------------------------
class Amenity(AuditMixin, Base):
    """
    A feature or facility that can be attached to a room type.

    System amenities (WiFi, TV, AC, Parking, Breakfast, Laundry) are seeded
    at startup and cannot be deleted.
    """

    __tablename__ = "amenities"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    icon: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Icon identifier (e.g. lucide icon name)",
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="System amenities cannot be deleted",
    )

    # Relationships
    room_types: Mapped[list["RoomType"]] = relationship(
        "RoomType",
        secondary=room_type_amenities,
        back_populates="amenities",
        lazy="selectin",
    )

    __table_args__ = (UniqueConstraint("name", name="uq_amenities_name"),)


# ---------------------------------------------------------------------------
# BedType
# ---------------------------------------------------------------------------
class BedType(AuditMixin, Base):
    """Bed configuration types (Single, Double, Queen, King, custom)."""

    __tablename__ = "bed_types"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    __table_args__ = (UniqueConstraint("name", name="uq_bed_types_name"),)


# ---------------------------------------------------------------------------
# RoomType
# ---------------------------------------------------------------------------
class RoomType(AuditMixin, Base):
    """
    Category of rooms sharing common pricing and characteristics.

    Examples: Standard, Deluxe, Suite, Executive, Villa.
    """

    __tablename__ = "room_types"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    base_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Default weekday price per night",
    )
    weekend_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Override price for weekends; NULL = use base_price",
    )
    max_occupancy: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=2,
    )
    extra_bed_allowed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    extra_bed_charge: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        comment="active | inactive",
    )

    # Relationships
    amenities: Mapped[list["Amenity"]] = relationship(
        "Amenity",
        secondary=room_type_amenities,
        back_populates="room_types",
        lazy="selectin",
    )
    images: Mapped[list["RoomTypeImage"]] = relationship(
        "RoomTypeImage",
        back_populates="room_type",
        cascade="all, delete-orphan",
        order_by="RoomTypeImage.display_order",
        lazy="selectin",
    )
    rooms: Mapped[list["Room"]] = relationship(
        "Room",
        back_populates="room_type",
        lazy="dynamic",
    )
    rate_plan_rates: Mapped[list["RatePlanSeasonRate"]] = relationship(
        "RatePlanSeasonRate",
        back_populates="room_type",
        lazy="dynamic",
    )

    __table_args__ = (UniqueConstraint("name", name="uq_room_types_name"),)


# ---------------------------------------------------------------------------
# RoomTypeImage
# ---------------------------------------------------------------------------
class RoomTypeImage(Base):
    """Image gallery entries for a room type."""

    __tablename__ = "room_type_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("room_types.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_url: Mapped[str] = mapped_column(String(512), nullable=False)
    caption: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    room_type: Mapped["RoomType"] = relationship("RoomType", back_populates="images")


# ---------------------------------------------------------------------------
# Room
# ---------------------------------------------------------------------------
class Room(AuditMixin, Base):
    """Individual physical room in the hotel."""

    __tablename__ = "rooms"

    room_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Unique room identifier (e.g. '101', 'V01')",
    )
    floor_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("floors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    room_type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("room_types.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=2,
    )
    view: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="e.g. Sea View, Garden View, City View",
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="available",
        comment="available | occupied | out_of_order",
    )
    housekeeping_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="clean",
        comment="clean | dirty | inspected | out_of_service",
    )
    maintenance_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="operational",
        comment="operational | under_maintenance | out_of_order",
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    floor: Mapped[Optional["Floor"]] = relationship("Floor", back_populates="rooms")
    room_type: Mapped["RoomType"] = relationship("RoomType", back_populates="rooms")

    __table_args__ = (
        UniqueConstraint("room_number", name="uq_rooms_room_number"),
        Index("ix_rooms_status", "status"),
        Index("ix_rooms_housekeeping_status", "housekeeping_status"),
        Index("ix_rooms_maintenance_status", "maintenance_status"),
    )


# ---------------------------------------------------------------------------
# Tax
# ---------------------------------------------------------------------------
class Tax(AuditMixin, Base):
    """
    Tax rule applicable to room charges, F&B, etc.

    type = 'percentage' → rate is % (e.g. 18.00 = 18%)
    type = 'fixed'      → rate is a fixed INR amount per transaction
    """

    __tablename__ = "taxes"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Short machine-safe code, e.g. GST18",
    )
    tax_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="percentage",
        comment="percentage | fixed",
    )
    rate: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=False,
        comment="Percentage value OR fixed amount depending on tax_type",
    )
    is_inclusive: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="True = already included in price; False = added on top",
    )
    applies_to: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="all",
        comment="all | rooms | restaurant | services",
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("code", name="uq_taxes_code"),
    )


# ---------------------------------------------------------------------------
# PaymentMethod
# ---------------------------------------------------------------------------
class PaymentMethod(AuditMixin, Base):
    """Accepted payment methods (Cash, UPI, Card, etc.)."""

    __tablename__ = "payment_methods"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Machine-safe code: cash, upi, credit_card, …",
    )
    payment_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="cash | upi | credit_card | debit_card | net_banking | wallet | bank_transfer | other",
    )
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="System methods cannot be deleted",
    )
    requires_reference: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="Collect transaction reference/UTR when using this method",
    )
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (UniqueConstraint("code", name="uq_payment_methods_code"),)


# ---------------------------------------------------------------------------
# Currency
# ---------------------------------------------------------------------------
class Currency(AuditMixin, Base):
    """Supported currencies for multi-currency billing."""

    __tablename__ = "currencies"

    code: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        comment="ISO 4217 code e.g. INR, USD",
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    symbol: Mapped[str] = mapped_column(String(5), nullable=False)
    exchange_rate: Mapped[Decimal] = mapped_column(
        Numeric(16, 6),
        nullable=False,
        default=Decimal("1.0"),
        comment="Rate relative to base currency",
    )
    decimal_places: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="Exactly one currency must be marked as default",
    )

    __table_args__ = (UniqueConstraint("code", name="uq_currencies_code"),)


# ---------------------------------------------------------------------------
# Season
# ---------------------------------------------------------------------------
class Season(AuditMixin, Base):
    """
    Date-range pricing season.

    Seasons are non-overlapping periods used to apply different rate plans.
    The service layer enforces no-overlap validation.
    """

    __tablename__ = "seasons"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Higher priority wins if dates overlap",
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    rate_plan_rates: Mapped[list["RatePlanSeasonRate"]] = relationship(
        "RatePlanSeasonRate",
        back_populates="season",
        lazy="dynamic",
    )

    __table_args__ = (
        Index("ix_seasons_start_date", "start_date"),
        Index("ix_seasons_end_date", "end_date"),
    )


# ---------------------------------------------------------------------------
# RatePlan
# ---------------------------------------------------------------------------
class RatePlan(AuditMixin, Base):
    """
    Named pricing plan (e.g. Standard, EP, MAP, AP, Corporate).

    Each plan has per-season, per-room-type pricing rows in RatePlanSeasonRate.
    """

    __tablename__ = "rate_plans"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meal_plan: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="EP",
        comment="EP (no meals) | CP (breakfast) | MAP (B+D) | AP (all meals)",
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    min_stay_nights: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    max_stay_nights: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cancellation_policy: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    season_rates: Mapped[list["RatePlanSeasonRate"]] = relationship(
        "RatePlanSeasonRate",
        back_populates="rate_plan",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (UniqueConstraint("code", name="uq_rate_plans_code"),)


# ---------------------------------------------------------------------------
# RatePlanSeasonRate
# ---------------------------------------------------------------------------
class RatePlanSeasonRate(Base):
    """
    Pricing matrix: rate_plan × season × room_type = nightly price.

    When season_id IS NULL, the row is the default (off-season) price.
    """

    __tablename__ = "rate_plan_season_rates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rate_plan_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rate_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    room_type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("room_types.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    season_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("seasons.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    price_per_night: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    weekend_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Weekend override; NULL = use price_per_night",
    )
    extra_person_charge: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    # Relationships
    rate_plan: Mapped["RatePlan"] = relationship("RatePlan", back_populates="season_rates")
    room_type: Mapped["RoomType"] = relationship("RoomType", back_populates="rate_plan_rates")
    season: Mapped[Optional["Season"]] = relationship("Season", back_populates="rate_plan_rates")

    __table_args__ = (
        UniqueConstraint(
            "rate_plan_id", "room_type_id", "season_id",
            name="uq_rate_plan_season_rates",
        ),
    )
