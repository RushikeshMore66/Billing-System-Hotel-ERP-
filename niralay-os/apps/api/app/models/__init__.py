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

# ── File Uploads (must come before models that FK into it) ───────────────────
from app.models.file_upload import UploadedFile

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

# ── Inventory ────────────────────────────────────────────────────────────────
from app.models.inventory import (
    InventoryCategory,
    StoreLocation,
    InventoryItem,
    StockMovement,
)

# ── Expenses ─────────────────────────────────────────────────────────────────
from app.models.expense import ExpenseCategory, Expense

# ── Billing ──────────────────────────────────────────────────────────────────
from app.models.billing import Bill, BillItem, Payment

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
    # file uploads
    "UploadedFile",
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
    # inventory
    "InventoryCategory",
    "StoreLocation",
    "InventoryItem",
    "StockMovement",
    # expenses
    "ExpenseCategory",
    "Expense",
    # billing
    "Bill",
    "BillItem",
    "Payment",
]
