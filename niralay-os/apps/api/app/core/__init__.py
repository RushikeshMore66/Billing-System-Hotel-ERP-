"""
app.core — Core application layer.

Public API for this package. Other packages import from here.
"""

from app.core.environment import Environment
from app.core.settings import Settings, get_settings, settings
from app.core.constants import (
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
    API_VERSION,
    API_PREFIX,
)

__all__ = [
    # Environment
    "Environment",
    # Settings
    "Settings",
    "get_settings",
    "settings",
    # Domain constants
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
