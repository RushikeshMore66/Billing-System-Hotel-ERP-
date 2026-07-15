"""
Application-wide constants for NiralayOS.
"""

from enum import Enum

API_VERSION: str = "v1"
API_PREFIX: str = f"/api/{API_VERSION}"

DATE_FORMAT: str = "%Y-%m-%d"
DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S"
DISPLAY_DATE_FORMAT: str = "%d %b %Y"
DEFAULT_TIMEZONE: str = "Asia/Kolkata"
DEFAULT_LANGUAGE: str = "en"

DEFAULT_CURRENCY: str = "INR"
DEFAULT_CURRENCY_SYMBOL: str = "INR"
GST_RATES: tuple = (0.0, 5.0, 12.0, 18.0, 28.0)
DEFAULT_GST_RATE: float = 18.0

DEFAULT_PAGE: int = 1
DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 200

PASSWORD_MIN_LENGTH: int = 8
PASSWORD_MAX_LENGTH: int = 128
BCRYPT_ROUNDS: int = 12
TOKEN_TYPE_BEARER: str = "bearer"


class Role(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    RECEPTIONIST = "receptionist"
    CASHIER = "cashier"
    WAITER = "waiter"
    CHEF = "chef"
    HOUSEKEEPING = "housekeeping"
    ACCOUNTANT = "accountant"
    VIEWER = "viewer"


ROLE_HIERARCHY: dict = {
    Role.SUPER_ADMIN: 100,
    Role.ADMIN: 90,
    Role.MANAGER: 70,
    Role.ACCOUNTANT: 60,
    Role.RECEPTIONIST: 50,
    Role.CASHIER: 50,
    Role.CHEF: 40,
    Role.WAITER: 30,
    Role.HOUSEKEEPING: 20,
    Role.VIEWER: 10,
}


class Permission(str, Enum):
    DASHBOARD_VIEW = "dashboard:view"
    ROOM_VIEW = "room:view"
    ROOM_CREATE = "room:create"
    ROOM_UPDATE = "room:update"
    ROOM_DELETE = "room:delete"
    RESERVATION_VIEW = "reservation:view"
    RESERVATION_CREATE = "reservation:create"
    RESERVATION_UPDATE = "reservation:update"
    RESERVATION_DELETE = "reservation:delete"
    RESERVATION_CHECKIN = "reservation:checkin"
    RESERVATION_CHECKOUT = "reservation:checkout"
    BILL_VIEW = "bill:view"
    BILL_CREATE = "bill:create"
    BILL_UPDATE = "bill:update"
    BILL_VOID = "bill:void"
    BILL_PRINT = "bill:print"
    ORDER_VIEW = "order:view"
    ORDER_CREATE = "order:create"
    ORDER_UPDATE = "order:update"
    ORDER_CANCEL = "order:cancel"
    INVENTORY_VIEW = "inventory:view"
    INVENTORY_CREATE = "inventory:create"
    INVENTORY_UPDATE = "inventory:update"
    EMPLOYEE_VIEW = "employee:view"
    EMPLOYEE_CREATE = "employee:create"
    EMPLOYEE_UPDATE = "employee:update"
    EMPLOYEE_DELETE = "employee:delete"
    FINANCE_VIEW = "finance:view"
    FINANCE_MANAGE = "finance:manage"
    REPORT_VIEW = "report:view"
    REPORT_EXPORT = "report:export"
    SETTINGS_VIEW = "settings:view"
    SETTINGS_MANAGE = "settings:manage"
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"


ROLE_PERMISSIONS: dict = {
    Role.SUPER_ADMIN: [p.value for p in Permission],
    Role.ADMIN: [p.value for p in Permission if p not in (Permission.SETTINGS_MANAGE,)],
    Role.MANAGER: [
        Permission.DASHBOARD_VIEW, Permission.ROOM_VIEW, Permission.ROOM_CREATE, Permission.ROOM_UPDATE,
        Permission.RESERVATION_VIEW, Permission.RESERVATION_CREATE, Permission.RESERVATION_UPDATE,
        Permission.RESERVATION_CHECKIN, Permission.RESERVATION_CHECKOUT,
        Permission.BILL_VIEW, Permission.BILL_CREATE, Permission.BILL_PRINT,
        Permission.ORDER_VIEW, Permission.ORDER_CREATE, Permission.ORDER_UPDATE,
        Permission.INVENTORY_VIEW, Permission.INVENTORY_CREATE, Permission.INVENTORY_UPDATE,
        Permission.EMPLOYEE_VIEW, Permission.FINANCE_VIEW,
        Permission.REPORT_VIEW, Permission.REPORT_EXPORT, Permission.SETTINGS_VIEW, Permission.USER_VIEW,
    ],
    Role.RECEPTIONIST: [
        Permission.DASHBOARD_VIEW, Permission.ROOM_VIEW,
        Permission.RESERVATION_VIEW, Permission.RESERVATION_CREATE, Permission.RESERVATION_UPDATE,
        Permission.RESERVATION_CHECKIN, Permission.RESERVATION_CHECKOUT,
        Permission.BILL_VIEW, Permission.BILL_CREATE, Permission.BILL_PRINT,
    ],
    Role.CASHIER: [
        Permission.DASHBOARD_VIEW, Permission.BILL_VIEW, Permission.BILL_CREATE,
        Permission.BILL_UPDATE, Permission.BILL_PRINT, Permission.ORDER_VIEW,
    ],
    Role.WAITER: [Permission.ORDER_VIEW, Permission.ORDER_CREATE, Permission.ORDER_UPDATE],
    Role.CHEF: [Permission.ORDER_VIEW, Permission.ORDER_UPDATE, Permission.INVENTORY_VIEW],
    Role.HOUSEKEEPING: [Permission.ROOM_VIEW, Permission.ROOM_UPDATE],
    Role.ACCOUNTANT: [
        Permission.DASHBOARD_VIEW, Permission.BILL_VIEW, Permission.BILL_PRINT,
        Permission.FINANCE_VIEW, Permission.FINANCE_MANAGE,
        Permission.REPORT_VIEW, Permission.REPORT_EXPORT,
    ],
    Role.VIEWER: [
        Permission.DASHBOARD_VIEW, Permission.ROOM_VIEW,
        Permission.RESERVATION_VIEW, Permission.BILL_VIEW, Permission.REPORT_VIEW,
    ],
}


class RoomStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    CLEANING = "cleaning"
    MAINTENANCE = "maintenance"
    BLOCKED = "blocked"


class RoomType(str, Enum):
    STANDARD = "standard"
    DELUXE = "deluxe"
    SUITE = "suite"
    PRESIDENTIAL = "presidential"
    DORMITORY = "dormitory"
    COTTAGE = "cottage"


class ReservationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class ReservationSource(str, Enum):
    DIRECT = "direct"
    WALK_IN = "walk_in"
    PHONE = "phone"
    OTA = "ota"
    CORPORATE = "corporate"
    AGENT = "agent"


class BillStatus(str, Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    VOID = "void"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    NET_BANKING = "net_banking"
    CHEQUE = "cheque"
    CREDIT = "credit"


class OrderStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"
    CANCELLED = "cancelled"


class TableStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    CLEANING = "cleaning"


UPLOAD_ALLOWED_EXTENSIONS: frozenset = frozenset(
    {".jpg", ".jpeg", ".png", ".webp", ".pdf", ".xlsx", ".csv"}
)
MAX_UPLOAD_SIZE_MB: int = 10
MAX_UPLOAD_SIZE_BYTES: int = MAX_UPLOAD_SIZE_MB * 1024 * 1024

AUDIT_FIELDS: tuple = (
    "id", "uuid", "created_at", "updated_at",
    "created_by", "updated_by", "deleted_at", "is_active",
)
