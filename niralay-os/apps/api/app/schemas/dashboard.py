"""
Dashboard response schemas for NiralayOS.

All schemas are pure read-only (response only). They have no Create/Update
counterparts because the dashboard is a read-only aggregate view.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# KPI / Overview
# ---------------------------------------------------------------------------
class KPIRevenue(BaseModel):
    today: float = Field(..., description="Today's total revenue in INR")
    yesterday: float = Field(..., description="Yesterday's total revenue in INR")
    change_pct: float = Field(..., description="% change vs yesterday, e.g. 18.4")
    hotel_revenue: float
    restaurant_revenue: float
    other_revenue: float


class KPIOccupancy(BaseModel):
    total_rooms: int
    occupied_rooms: int
    available_rooms: int
    occupancy_pct: float = Field(..., description="Occupied / Total * 100")
    current_guests: int


class KPIReservation(BaseModel):
    today_total: int = Field(..., description="All reservations with arrival today")
    today_checkins: int = Field(..., description="Today's check-ins (confirmed/pending)")
    today_checkouts: int = Field(..., description="Today's check-outs")
    pending_arrivals: int = Field(..., description="Arriving today, not yet checked in")


class KPIRestaurant(BaseModel):
    active_orders: int
    today_revenue: float
    dine_in_orders: int
    room_service_orders: int
    takeaway_orders: int


class KPIFinance(BaseModel):
    pending_payments: float = Field(..., description="Sum of unpaid bills in INR")
    pending_count: int
    monthly_revenue: float
    net_profit_est: float = Field(..., description="Monthly revenue minus 70% COGS estimate")


class KPIInventory(BaseModel):
    low_stock_count: int
    critical_count: int
    ok_count: int


class KPIEmployee(BaseModel):
    total_active: int
    present_today: int
    on_leave: int


class DashboardKPIs(BaseModel):
    revenue: KPIRevenue
    occupancy: KPIOccupancy
    reservation: KPIReservation
    restaurant: KPIRestaurant
    finance: KPIFinance
    inventory: KPIInventory
    employee: KPIEmployee
    as_of: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Chart data points
# ---------------------------------------------------------------------------
class RevenueTrendPoint(BaseModel):
    day: str = Field(..., description="Day label, e.g. Mon")
    date: date
    revenue: float
    last_week: float


class OccupancyTrendPoint(BaseModel):
    hour: str = Field(..., description="Time label, e.g. 9am")
    hotel_pct: float
    restaurant_pct: float


class ReservationTrendPoint(BaseModel):
    date: date
    new_reservations: int
    check_ins: int
    check_outs: int


class CashFlowPoint(BaseModel):
    date: date
    inflow: float
    outflow: float
    net: float


class MonthlyRevenuePoint(BaseModel):
    month: str = Field(..., description="e.g. Jan")
    year: int
    total: float
    hotel: float
    restaurant: float


class DashboardCharts(BaseModel):
    revenue_trend: list[RevenueTrendPoint]
    occupancy_trend: list[OccupancyTrendPoint]
    reservation_trend: list[ReservationTrendPoint]
    cash_flow_trend: list[CashFlowPoint]
    monthly_revenue: list[MonthlyRevenuePoint]


# ---------------------------------------------------------------------------
# Recent Reservations (for dashboard table)
# ---------------------------------------------------------------------------
class DashboardReservation(BaseModel):
    id: int
    reservation_number: str
    guest_name: str
    room_number: Optional[str] = None
    room_type: Optional[str] = None
    check_in: date
    check_out: date
    nights: int
    amount: float
    status: str
    source: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Inventory Alert
# ---------------------------------------------------------------------------
class InventoryAlert(BaseModel):
    id: int
    item_name: str
    current_quantity: float
    unit: str
    minimum_quantity: float
    level: str = Field(..., description="critical | low | ok")
    category: Optional[str] = None


# ---------------------------------------------------------------------------
# Activity Feed
# ---------------------------------------------------------------------------
class ActivityItem(BaseModel):
    id: int
    event_type: str = Field(
        ...,
        description=(
            "reservation_created | guest_checked_in | guest_checked_out | "
            "restaurant_bill | invoice_paid | room_cleaned | inventory_purchased | employee_clock_in"
        ),
    )
    description: str
    actor: Optional[str] = None
    resource_id: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    occurred_at: datetime


# ---------------------------------------------------------------------------
# Widget responses (one per endpoint)
# ---------------------------------------------------------------------------
class RevenueWidget(BaseModel):
    kpi: KPIRevenue
    trend: list[RevenueTrendPoint]
    monthly: list[MonthlyRevenuePoint]


class OccupancyWidget(BaseModel):
    kpi: KPIOccupancy
    trend: list[OccupancyTrendPoint]


class ReservationWidget(BaseModel):
    kpi: KPIReservation
    today_reservations: list[DashboardReservation]
    trend: list[ReservationTrendPoint]


class RestaurantWidget(BaseModel):
    kpi: KPIRestaurant
    trend: list[RevenueTrendPoint]


class FinanceWidget(BaseModel):
    kpi: KPIFinance
    cash_flow: list[CashFlowPoint]


class InventoryWidget(BaseModel):
    kpi: KPIInventory
    alerts: list[InventoryAlert]


class EmployeeWidget(BaseModel):
    kpi: KPIEmployee


class ActivityWidget(BaseModel):
    activities: list[ActivityItem]
    total: int


class DashboardOverview(BaseModel):
    """Complete dashboard — all widgets combined."""
    kpis: DashboardKPIs
    today_reservations: list[DashboardReservation]
    inventory_alerts: list[InventoryAlert]
    recent_activities: list[ActivityItem]
    charts: DashboardCharts
    as_of: datetime = Field(default_factory=datetime.utcnow)
