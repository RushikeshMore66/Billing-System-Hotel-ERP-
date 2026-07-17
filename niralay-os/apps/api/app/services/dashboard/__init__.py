"""
Dashboard services package for NiralayOS.

Each widget has its own service module.  Business logic lives here;
repositories handle only DB I/O.
"""

from app.services.dashboard.overview import DashboardOverviewService
from app.services.dashboard.revenue import RevenueService
from app.services.dashboard.occupancy import OccupancyService
from app.services.dashboard.reservation import ReservationService
from app.services.dashboard.restaurant import RestaurantService
from app.services.dashboard.finance import FinanceService
from app.services.dashboard.inventory import InventoryService
from app.services.dashboard.employee import EmployeeService
from app.services.dashboard.activity import ActivityService

__all__ = [
    "DashboardOverviewService",
    "RevenueService",
    "OccupancyService",
    "ReservationService",
    "RestaurantService",
    "FinanceService",
    "InventoryService",
    "EmployeeService",
    "ActivityService",
]
