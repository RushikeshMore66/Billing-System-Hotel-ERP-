"""
Models package for NiralayOS.

Import all models here so that:
  1. SQLAlchemy's mapper registry is populated before Alembic runs autogenerate.
  2. Relationship back-refs resolve correctly at runtime.

Usage:
    from app.models import User, Role, Room, MenuItem, Department, BusinessSettings
"""

# ── Sprint 2: Identity & Access ─────────────────────────────────────────────
from app.models.user import User, PasswordHistory, UserPreference, user_roles
from app.models.role import Role, Permission, role_permissions
from app.models.session import Session, RefreshToken
from app.models.audit_log import AuditLog

# ── Sprint 3: Property Configuration ────────────────────────────────────────
from app.models.property import (
    PropertyProfile,
    Floor,
    Amenity,
    BedType,
    RoomType,
    RoomTypeImage,
    Room,
    Tax,
    PaymentMethod,
    Currency,
    Season,
    RatePlan,
    RatePlanSeasonRate,
    room_type_amenities,
)
from app.models.restaurant import (
    RestaurantCategory,
    MenuCategory,
    KitchenStation,
    MenuItem,
    MenuModifier,
    MenuModifierOption,
    RestaurantTable,
    menu_item_modifiers,
)
from app.models.organization import Department, Designation, GuestIDType
from app.models.settings import BusinessSettings

# ── Phase 2: Reservations ───────────────────────────────────────────────────
from app.models.guest import Guest
from app.models.reservation import Reservation, ReservationStatusHistory

__all__ = [
    # identity
    "User",
    "PasswordHistory",
    "UserPreference",
    "user_roles",
    "Role",
    "Permission",
    "role_permissions",
    "Session",
    "RefreshToken",
    "AuditLog",
    # property config
    "PropertyProfile",
    "Floor",
    "Amenity",
    "BedType",
    "RoomType",
    "RoomTypeImage",
    "Room",
    "Tax",
    "PaymentMethod",
    "Currency",
    "Season",
    "RatePlan",
    "RatePlanSeasonRate",
    "room_type_amenities",
    # restaurant
    "RestaurantCategory",
    "MenuCategory",
    "KitchenStation",
    "MenuItem",
    "MenuModifier",
    "MenuModifierOption",
    "RestaurantTable",
    "menu_item_modifiers",
    # organisation
    "Department",
    "Designation",
    "GuestIDType",
    # settings
    "BusinessSettings",
    # reservations
    "Guest",
    "Reservation",
    "ReservationStatusHistory",
]
