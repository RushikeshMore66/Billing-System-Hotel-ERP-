"""Schemas package for NiralayOS."""

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

