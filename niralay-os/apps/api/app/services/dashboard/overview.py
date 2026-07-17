"""
Dashboard overview service for NiralayOS.

Composes all widget services into a single aggregated response.
Uses one DB connection for all sub-service calls to avoid redundant connections.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.schemas.dashboard import DashboardCharts, DashboardOverview
from app.services.dashboard.activity import ActivityService
from app.services.dashboard.employee import EmployeeService
from app.services.dashboard.finance import FinanceService
from app.services.dashboard.inventory import InventoryService
from app.services.dashboard.occupancy import OccupancyService
from app.services.dashboard.reservation import ReservationService
from app.services.dashboard.restaurant import RestaurantService
from app.services.dashboard.revenue import RevenueService
from app.schemas.dashboard import DashboardKPIs


class DashboardOverviewService:
    """
    Orchestrates all widget services to build the full dashboard payload.

    All child services share the same DB session to avoid N+1 connections.
    """

    def __init__(self, db: Session) -> None:
        self._db = db
        self._revenue = RevenueService(db)
        self._occupancy = OccupancyService(db)
        self._reservation = ReservationService(db)
        self._restaurant = RestaurantService(db)
        self._finance = FinanceService(db)
        self._inventory = InventoryService(db)
        self._employee = EmployeeService(db)
        self._activity = ActivityService(db)

    def get_overview(self) -> DashboardOverview:
        """
        Build the complete dashboard overview.

        Executes each widget service once. The result is a fully populated
        DashboardOverview that satisfies every KPI card, chart, and table
        on the frontend dashboard page without any further API calls.
        """
        revenue_widget = self._revenue.get_widget()
        occupancy_widget = self._occupancy.get_widget()
        reservation_widget = self._reservation.get_widget()
        restaurant_widget = self._restaurant.get_widget()
        finance_widget = self._finance.get_widget()
        inventory_widget = self._inventory.get_widget()
        employee_widget = self._employee.get_widget()
        activity_widget = self._activity.get_widget(limit=20)

        kpis = DashboardKPIs(
            revenue=revenue_widget.kpi,
            occupancy=occupancy_widget.kpi,
            reservation=reservation_widget.kpi,
            restaurant=restaurant_widget.kpi,
            finance=finance_widget.kpi,
            inventory=inventory_widget.kpi,
            employee=employee_widget.kpi,
            as_of=datetime.now(timezone.utc),
        )

        charts = DashboardCharts(
            revenue_trend=revenue_widget.trend,
            occupancy_trend=occupancy_widget.trend,
            reservation_trend=reservation_widget.trend,
            cash_flow_trend=finance_widget.cash_flow,
            monthly_revenue=revenue_widget.monthly,
        )

        return DashboardOverview(
            kpis=kpis,
            today_reservations=reservation_widget.today_reservations,
            inventory_alerts=inventory_widget.alerts,
            recent_activities=activity_widget.activities[:10],
            charts=charts,
            as_of=datetime.now(timezone.utc),
        )
