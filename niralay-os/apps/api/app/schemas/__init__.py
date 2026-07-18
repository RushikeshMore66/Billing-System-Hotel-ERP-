"""Schemas package for NiralayOS."""

# ── Sprint 3: Property Configuration ─────────────────────────────────────────
from app.schemas.property import (
    PropertyProfileUpdate,
    PropertyProfileOut,
    FloorCreate, FloorUpdate, FloorOut,
    AmenityCreate, AmenityUpdate, AmenityOut,
    BedTypeCreate, BedTypeUpdate, BedTypeOut,
    RoomTypeCreate, RoomTypeUpdate, RoomTypeOut, RoomTypeBrief,
    RoomTypeImageIn, RoomTypeImageOut,
    RoomCreate, RoomUpdate, RoomOut, RoomBulkCreate, RoomBulkResult,
    TaxCreate, TaxUpdate, TaxOut,
    PaymentMethodCreate, PaymentMethodUpdate, PaymentMethodOut,
    CurrencyCreate, CurrencyUpdate, CurrencyOut,
    SeasonCreate, SeasonUpdate, SeasonOut,
    RatePlanCreate, RatePlanUpdate, RatePlanOut,
    RatePlanSeasonRateIn, RatePlanSeasonRateOut,
)
from app.schemas.restaurant import (
    RestaurantCategoryCreate, RestaurantCategoryUpdate, RestaurantCategoryOut,
    MenuCategoryCreate, MenuCategoryUpdate, MenuCategoryOut,
    KitchenStationCreate, KitchenStationUpdate, KitchenStationOut,
    MenuItemCreate, MenuItemUpdate, MenuItemOut,
    MenuModifierCreate, MenuModifierUpdate, MenuModifierOut, MenuModifierBrief,
    MenuModifierOptionIn, MenuModifierOptionOut,
    RestaurantTableCreate, RestaurantTableUpdate, RestaurantTableOut,
)
from app.schemas.organization import (
    DepartmentCreate, DepartmentUpdate, DepartmentOut,
    DesignationCreate, DesignationUpdate, DesignationOut,
    GuestIDTypeCreate, GuestIDTypeUpdate, GuestIDTypeOut,
)
from app.schemas.business_settings import BusinessSettingsUpdate, BusinessSettingsOut

from app.schemas.base import (
    AuditSchema,
    ErrorDetail,
    ErrorResponse,
    IDSchema,
    PaginatedResponse,
    ResponseMeta,
    SuccessResponse,
    TimestampSchema,
)
from app.schemas.auth import (
    ChangePasswordRequest,
    CurrentUserResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.user import UserCreate, UserListOut, UserOut, UserUpdate, RoleInUser
from app.schemas.role import (
    AssignPermissionsRequest,
    AssignRoleRequest,
    PermissionCreate,
    PermissionOut,
    RoleCreate,
    RoleOut,
    RoleUpdate,
    RoleWithPermissions,
)
from app.schemas.session import AuditLogOut, SessionOut
from app.schemas.dashboard import (
    ActivityItem,
    ActivityWidget,
    CashFlowPoint,
    DashboardCharts,
    DashboardKPIs,
    DashboardOverview,
    DashboardReservation,
    EmployeeWidget,
    FinanceWidget,
    InventoryAlert,
    InventoryWidget,
    KPIEmployee,
    KPIFinance,
    KPIInventory,
    KPIOccupancy,
    KPIReservation,
    KPIRestaurant,
    KPIRevenue,
    MonthlyRevenuePoint,
    OccupancyTrendPoint,
    OccupancyWidget,
    ReservationTrendPoint,
    ReservationWidget,
    RestaurantWidget,
    RevenueWidget,
    RevenueTrendPoint,
)

__all__ = [
    # base
    "AuditSchema", "ErrorDetail", "ErrorResponse", "IDSchema",
    "PaginatedResponse", "ResponseMeta", "SuccessResponse",
    "TimestampSchema",
    # auth
    "ChangePasswordRequest", "CurrentUserResponse", "ForgotPasswordRequest",
    "LoginRequest", "MessageResponse", "RefreshRequest",
    "ResetPasswordRequest", "TokenResponse",
    # user
    "UserCreate", "UserListOut", "UserOut", "UserUpdate", "RoleInUser",
    # role / permission
    "AssignPermissionsRequest", "AssignRoleRequest",
    "PermissionCreate", "PermissionOut",
    "RoleCreate", "RoleOut", "RoleUpdate", "RoleWithPermissions",
    # session / audit
    "AuditLogOut", "SessionOut",
    # dashboard
    "ActivityItem", "ActivityWidget", "CashFlowPoint", "DashboardCharts",
    "DashboardKPIs", "DashboardOverview", "DashboardReservation",
    "EmployeeWidget", "FinanceWidget", "InventoryAlert", "InventoryWidget",
    "KPIEmployee", "KPIFinance", "KPIInventory", "KPIOccupancy",
    "KPIReservation", "KPIRestaurant", "KPIRevenue", "MonthlyRevenuePoint",
    "OccupancyTrendPoint", "OccupancyWidget", "ReservationTrendPoint",
    "ReservationWidget", "RestaurantWidget", "RevenueWidget", "RevenueTrendPoint",
]

