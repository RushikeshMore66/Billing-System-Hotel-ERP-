"""
Dashboard router for NiralayOS — /api/v1/dashboard/*

Endpoints:
    GET  /dashboard/overview        — Full dashboard (all widgets combined)
    GET  /dashboard/revenue         — Revenue widget
    GET  /dashboard/occupancy       — Occupancy widget
    GET  /dashboard/reservations    — Reservation widget
    GET  /dashboard/restaurant      — Restaurant widget
    GET  /dashboard/finance         — Finance widget
    GET  /dashboard/inventory       — Inventory widget
    GET  /dashboard/employees       — Employee widget
    GET  /dashboard/activity        — Activity feed
    GET  /dashboard/widgets         — Lightweight widget manifest

All endpoints require at minimum a valid authenticated session.
Specific widgets filter their payload based on the caller's role.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_active_user,
    get_db,
    require_permission,
)
from app.models.user import User
from app.schemas.base import SuccessResponse
from app.schemas.dashboard import (
    ActivityWidget,
    DashboardOverview,
    EmployeeWidget,
    FinanceWidget,
    InventoryWidget,
    OccupancyWidget,
    ReservationWidget,
    RestaurantWidget,
    RevenueWidget,
)
from app.services.dashboard import (
    ActivityService,
    DashboardOverviewService,
    EmployeeService,
    FinanceService,
    InventoryService,
    OccupancyService,
    ReservationService,
    RestaurantService,
    RevenueService,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# ---------------------------------------------------------------------------
# Overview — aggregates every widget in one call
# ---------------------------------------------------------------------------
@router.get(
    "/overview",
    response_model=SuccessResponse[DashboardOverview],
    status_code=status.HTTP_200_OK,
    summary="Full dashboard overview",
    description=(
        "Returns all KPI cards, chart data, recent reservations, inventory alerts, "
        "and activity feed in a single response. Requires `dashboard:view` permission."
    ),
)
def get_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("dashboard:view")),
) -> SuccessResponse[DashboardOverview]:
    svc = DashboardOverviewService(db)
    data = svc.get_overview()
    return SuccessResponse.of(data=data, message="Dashboard overview loaded")


# ---------------------------------------------------------------------------
# Revenue widget
# ---------------------------------------------------------------------------
@router.get(
    "/revenue",
    response_model=SuccessResponse[RevenueWidget],
    status_code=status.HTTP_200_OK,
    summary="Revenue widget",
    description=(
        "Today's revenue KPI, 7-day trend, and 6-month breakdown. "
        "Requires `dashboard:view` or `finance:view` permission."
    ),
)
def get_revenue(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("dashboard:view")),
) -> SuccessResponse[RevenueWidget]:
    data = RevenueService(db).get_widget()
    return SuccessResponse.of(data=data, message="Revenue data loaded")


# ---------------------------------------------------------------------------
# Occupancy widget
# ---------------------------------------------------------------------------
@router.get(
    "/occupancy",
    response_model=SuccessResponse[OccupancyWidget],
    status_code=status.HTTP_200_OK,
    summary="Occupancy widget",
    description="Current hotel occupancy KPI and hourly trend.",
)
def get_occupancy(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("dashboard:view")),
) -> SuccessResponse[OccupancyWidget]:
    data = OccupancyService(db).get_widget()
    return SuccessResponse.of(data=data, message="Occupancy data loaded")


# ---------------------------------------------------------------------------
# Reservations widget
# ---------------------------------------------------------------------------
@router.get(
    "/reservations",
    response_model=SuccessResponse[ReservationWidget],
    status_code=status.HTTP_200_OK,
    summary="Reservations widget",
    description="Today's check-ins, check-outs, and reservation list.",
)
def get_reservations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("dashboard:view")),
) -> SuccessResponse[ReservationWidget]:
    data = ReservationService(db).get_widget()
    return SuccessResponse.of(data=data, message="Reservation data loaded")


# ---------------------------------------------------------------------------
# Restaurant widget
# ---------------------------------------------------------------------------
@router.get(
    "/restaurant",
    response_model=SuccessResponse[RestaurantWidget],
    status_code=status.HTTP_200_OK,
    summary="Restaurant widget",
    description="Active orders, restaurant revenue, and order type breakdown.",
)
def get_restaurant(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("dashboard:view")),
) -> SuccessResponse[RestaurantWidget]:
    data = RestaurantService(db).get_widget()
    return SuccessResponse.of(data=data, message="Restaurant data loaded")


# ---------------------------------------------------------------------------
# Finance widget
# ---------------------------------------------------------------------------
@router.get(
    "/finance",
    response_model=SuccessResponse[FinanceWidget],
    status_code=status.HTTP_200_OK,
    summary="Finance widget",
    description=(
        "Pending payments, monthly revenue, net profit estimate, and 30-day cash flow. "
        "Requires `finance:view` permission."
    ),
)
def get_finance(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("finance:view")),
) -> SuccessResponse[FinanceWidget]:
    data = FinanceService(db).get_widget()
    return SuccessResponse.of(data=data, message="Finance data loaded")


# ---------------------------------------------------------------------------
# Inventory widget
# ---------------------------------------------------------------------------
@router.get(
    "/inventory",
    response_model=SuccessResponse[InventoryWidget],
    status_code=status.HTTP_200_OK,
    summary="Inventory widget",
    description="Low-stock and critical alerts with item details.",
)
def get_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("inventory:view")),
) -> SuccessResponse[InventoryWidget]:
    data = InventoryService(db).get_widget()
    return SuccessResponse.of(data=data, message="Inventory data loaded")


# ---------------------------------------------------------------------------
# Employee widget
# ---------------------------------------------------------------------------
@router.get(
    "/employees",
    response_model=SuccessResponse[EmployeeWidget],
    status_code=status.HTTP_200_OK,
    summary="Employee widget",
    description="Employee presence, active count, and on-leave summary.",
)
def get_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("employee:view")),
) -> SuccessResponse[EmployeeWidget]:
    data = EmployeeService(db).get_widget()
    return SuccessResponse.of(data=data, message="Employee data loaded")


# ---------------------------------------------------------------------------
# Activity feed
# ---------------------------------------------------------------------------
@router.get(
    "/activity",
    response_model=SuccessResponse[ActivityWidget],
    status_code=status.HTTP_200_OK,
    summary="Activity feed",
    description=(
        "Recent system activity events, sorted newest first. "
        "Supports pagination via page and size query params."
    ),
)
def get_activity(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("dashboard:view")),
) -> SuccessResponse[ActivityWidget]:
    skip = (page - 1) * size
    data = ActivityService(db).get_widget(limit=size, skip=skip)
    return SuccessResponse.of(data=data, message="Activity feed loaded")


# ---------------------------------------------------------------------------
# Widget manifest — lightweight endpoint listing available widgets
# ---------------------------------------------------------------------------
@router.get(
    "/widgets",
    response_model=SuccessResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Widget manifest",
    description=(
        "Returns the list of available dashboard widgets and which permissions "
        "are required to access each one. Used by the frontend to conditionally "
        "render widgets based on the current user's role."
    ),
)
def get_widgets(
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[dict]:
    all_widgets = [
        {
            "id": "overview",
            "label": "Dashboard Overview",
            "endpoint": "/api/v1/dashboard/overview",
            "required_permission": "dashboard:view",
            "available": current_user.is_superuser or "dashboard:view" in current_user.permission_codes,
        },
        {
            "id": "revenue",
            "label": "Revenue",
            "endpoint": "/api/v1/dashboard/revenue",
            "required_permission": "dashboard:view",
            "available": current_user.is_superuser or "dashboard:view" in current_user.permission_codes,
        },
        {
            "id": "occupancy",
            "label": "Occupancy",
            "endpoint": "/api/v1/dashboard/occupancy",
            "required_permission": "dashboard:view",
            "available": current_user.is_superuser or "dashboard:view" in current_user.permission_codes,
        },
        {
            "id": "reservations",
            "label": "Reservations",
            "endpoint": "/api/v1/dashboard/reservations",
            "required_permission": "dashboard:view",
            "available": current_user.is_superuser or "dashboard:view" in current_user.permission_codes,
        },
        {
            "id": "restaurant",
            "label": "Restaurant",
            "endpoint": "/api/v1/dashboard/restaurant",
            "required_permission": "dashboard:view",
            "available": current_user.is_superuser or "dashboard:view" in current_user.permission_codes,
        },
        {
            "id": "finance",
            "label": "Finance",
            "endpoint": "/api/v1/dashboard/finance",
            "required_permission": "finance:view",
            "available": current_user.is_superuser or "finance:view" in current_user.permission_codes,
        },
        {
            "id": "inventory",
            "label": "Inventory Alerts",
            "endpoint": "/api/v1/dashboard/inventory",
            "required_permission": "inventory:view",
            "available": current_user.is_superuser or "inventory:view" in current_user.permission_codes,
        },
        {
            "id": "employees",
            "label": "Employees",
            "endpoint": "/api/v1/dashboard/employees",
            "required_permission": "employee:view",
            "available": current_user.is_superuser or "employee:view" in current_user.permission_codes,
        },
        {
            "id": "activity",
            "label": "Activity Feed",
            "endpoint": "/api/v1/dashboard/activity",
            "required_permission": "dashboard:view",
            "available": current_user.is_superuser or "dashboard:view" in current_user.permission_codes,
        },
    ]

    accessible = [w for w in all_widgets if w["available"]]
    return SuccessResponse.of(
        data={"widgets": accessible, "total": len(accessible)},
        message="Widget manifest loaded",
    )
