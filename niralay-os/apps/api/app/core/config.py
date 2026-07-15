"""
Application configuration facade.

Provides a single import point for configuration objects used
across the application. Consumers import from here, not from
individual modules, to keep the dependency surface clean.
"""

from app.core.settings import Settings, get_settings, settings
from app.core.environment import Environment
from app.core.constants import (
    API_VERSION,
    API_PREFIX,
    Role,
    Permission,
    ROLE_PERMISSIONS,
    RoomStatus,
    RoomType,
    ReservationStatus,
    ReservationSource,
    BillStatus,
    PaymentStatus,
    PaymentMethod,
    OrderStatus,
    TableStatus,
)

__all__ = [
    "Settings",
    "get_settings",
    "settings",
    "Environment",
    "API_VERSION",
    "API_PREFIX",
    "Role",
    "Permission",
    "ROLE_PERMISSIONS",
    "RoomStatus",
    "RoomType",
    "ReservationStatus",
    "ReservationSource",
    "BillStatus",
    "PaymentStatus",
    "PaymentMethod",
    "OrderStatus",
    "TableStatus",
]
