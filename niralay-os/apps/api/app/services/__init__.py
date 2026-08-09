"""Services package for NiralayOS."""

# ── Sprint 3: Property Configuration ────────────────────────────────────────
from app.services.property import (
    PropertyProfileService,
    FloorService,
    AmenityService,
    BedTypeService,
    RoomTypeService,
    RoomService,
    TaxService,
    PaymentMethodService,
    CurrencyService,
    SeasonService,
    RatePlanService,
)
from app.services.restaurant_config import (
    RestaurantCategoryService,
    MenuCategoryService,
    KitchenStationService,
    MenuItemService,
    MenuModifierService,
    RestaurantTableService,
)
from app.services.organization import DepartmentService, DesignationService, GuestIDTypeService
from app.services.business_settings import BusinessSettingsService

from app.services.audit import AuditService
from app.services.role import RoleService, PermissionService
from app.services.user import UserService
from app.services.auth import AuthService
from app.services.dashboard import (
    DashboardOverviewService,
    RevenueService,
    OccupancyService,
    ReservationService as DashboardReservationService,
    RestaurantService,
    FinanceService,
    InventoryService as DashboardInventoryService,
    EmployeeService,
    ActivityService,
)

# ── Sprint 5: Inventory, Expenses, Billing ───────────────────────────────────
from app.services.inventory import (
    InventoryCategoryService,
    StoreLocationService,
    InventoryItemService,
)
from app.services.expense import ExpenseCategoryService, ExpenseService
from app.services.billing import BillingService

__all__ = [
    "AuditService",
    "RoleService",
    "PermissionService",
    "UserService",
    "AuthService",
    "DashboardOverviewService",
    "RevenueService",
    "OccupancyService",
    "DashboardReservationService",
    "RestaurantService",
    "FinanceService",
    "DashboardInventoryService",
    "EmployeeService",
    "ActivityService",
    # Inventory
    "InventoryCategoryService",
    "StoreLocationService",
    "InventoryItemService",
    # Expenses
    "ExpenseCategoryService",
    "ExpenseService",
    # Billing
    "BillingService",
]

