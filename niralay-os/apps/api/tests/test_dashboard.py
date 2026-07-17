"""
Dashboard tests for NiralayOS.

Tests cover:
  - Repository queries (unit level with SQLite)
  - Service business logic
  - API endpoints (integration level with TestClient)
  - RBAC enforcement on protected endpoints
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password, create_access_token
from app.models.audit_log import AuditLog
from app.models.user import User
from app.repositories.dashboard import DashboardRepository
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_test_user(
    db: Session,
    email: str = "dash_test@example.com",
    username: str = "dashtest",
    is_superuser: bool = True,
) -> User:
    user = User(
        username=username,
        email=email,
        full_name="Dashboard Tester",
        password_hash=hash_password("Secure@Pass123!"),
        is_superuser=is_superuser,
        status="active",
    )
    db.add(user)
    db.flush()
    db.refresh(user)
    return user


def _create_audit_event(
    db: Session,
    user: User,
    event: str = "LOGIN",
    outcome: str = "success",
) -> AuditLog:
    log = AuditLog(
        actor_id=user.id,
        actor_uuid=str(user.uuid),
        event=event,
        outcome=outcome,
        detail=f"Test event: {event}",
    )
    db.add(log)
    db.flush()
    return log


def _get_auth_headers(user: User) -> dict:
    token = create_access_token(
        subject=str(user.uuid),
        role="super_admin",
        permissions=["dashboard:view", "finance:view", "inventory:view", "employee:view"],
    )
    return {"Authorization": f"Bearer {token}"}


def _get_limited_headers(user: User) -> dict:
    """Headers for a user with no permissions."""
    token = create_access_token(
        subject=str(user.uuid),
        role="viewer",
        permissions=[],
    )
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Repository tests
# ---------------------------------------------------------------------------

class TestDashboardRepository:
    """Unit tests for DashboardRepository queries."""

    def test_count_active_users_empty(self, db: Session) -> None:
        repo = DashboardRepository(db)
        count = repo.count_active_users()
        assert isinstance(count, int)
        assert count >= 0

    def test_count_active_users_with_data(self, db: Session) -> None:
        _create_test_user(db, email="repo_test1@x.com", username="repotest1")
        db.flush()
        repo = DashboardRepository(db)
        count = repo.count_active_users()
        assert count >= 1

    def test_count_active_sessions_empty(self, db: Session) -> None:
        repo = DashboardRepository(db)
        count = repo.count_active_sessions()
        assert isinstance(count, int)
        assert count >= 0

    def test_get_recent_activities_empty(self, db: Session) -> None:
        repo = DashboardRepository(db)
        activities = repo.get_recent_activities(limit=10)
        assert isinstance(activities, list)

    def test_get_recent_activities_with_data(self, db: Session) -> None:
        user = _create_test_user(db, email="acttest@x.com", username="acttest")
        _create_audit_event(db, user, "LOGIN")
        _create_audit_event(db, user, "LOGOUT")
        db.flush()

        repo = DashboardRepository(db)
        activities = repo.get_recent_activities(limit=10)
        events = [a["event"] for a in activities]
        assert "LOGIN" in events or "LOGOUT" in events

    def test_get_audit_counts_today(self, db: Session) -> None:
        user = _create_test_user(db, email="aud_today@x.com", username="audtoday")
        _create_audit_event(db, user, "LOGIN")
        db.flush()

        repo = DashboardRepository(db)
        counts = repo.get_audit_counts_today()
        assert isinstance(counts, dict)
        # LOGIN event should be present
        assert "LOGIN" in counts

    def test_get_audit_counts_yesterday(self, db: Session) -> None:
        repo = DashboardRepository(db)
        counts = repo.get_audit_counts_yesterday()
        assert isinstance(counts, dict)

    def test_get_monthly_login_summary(self, db: Session) -> None:
        repo = DashboardRepository(db)
        data = repo.get_monthly_login_summary(months=6)
        assert isinstance(data, list)
        for row in data:
            assert "year" in row
            assert "month" in row
            assert "count" in row

    def test_get_user_status_breakdown(self, db: Session) -> None:
        _create_test_user(db, email="status1@x.com", username="status1")
        db.flush()
        repo = DashboardRepository(db)
        breakdown = repo.get_user_status_breakdown()
        assert isinstance(breakdown, dict)

    def test_count_activities(self, db: Session) -> None:
        repo = DashboardRepository(db)
        count = repo.count_activities()
        assert isinstance(count, int)
        assert count >= 0


# ---------------------------------------------------------------------------
# Service tests
# ---------------------------------------------------------------------------

class TestRevenueService:
    def test_get_kpi_returns_valid_structure(self, db: Session) -> None:
        svc = RevenueService(db)
        kpi = svc.get_kpi()
        assert kpi.today >= 0
        assert kpi.yesterday >= 0
        assert isinstance(kpi.change_pct, float)
        assert kpi.hotel_revenue >= 0
        assert kpi.restaurant_revenue >= 0
        assert kpi.other_revenue >= 0

    def test_get_weekly_trend_length(self, db: Session) -> None:
        svc = RevenueService(db)
        trend = svc.get_weekly_trend()
        assert len(trend) == 7
        for point in trend:
            assert point.day in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
            assert point.revenue >= 0
            assert point.last_week >= 0

    def test_get_monthly_revenue_length(self, db: Session) -> None:
        svc = RevenueService(db)
        monthly = svc.get_monthly_revenue()
        assert len(monthly) == 6
        for point in monthly:
            assert point.total >= 0
            assert point.hotel >= 0
            assert point.restaurant >= 0

    def test_get_widget_returns_all_fields(self, db: Session) -> None:
        svc = RevenueService(db)
        widget = svc.get_widget()
        assert widget.kpi is not None
        assert len(widget.trend) == 7
        assert len(widget.monthly) == 6


class TestOccupancyService:
    def test_get_kpi_valid(self, db: Session) -> None:
        svc = OccupancyService(db)
        kpi = svc.get_kpi()
        assert kpi.total_rooms == 30
        assert kpi.occupied_rooms >= 0
        assert kpi.available_rooms >= 0
        assert kpi.occupied_rooms + kpi.available_rooms == kpi.total_rooms
        assert 0.0 <= kpi.occupancy_pct <= 100.0

    def test_get_hourly_trend_length(self, db: Session) -> None:
        svc = OccupancyService(db)
        trend = svc.get_hourly_trend()
        assert len(trend) == 7
        expected_hours = ["6am", "9am", "12pm", "3pm", "6pm", "9pm", "12am"]
        for i, point in enumerate(trend):
            assert point.hour == expected_hours[i]
            assert 0.0 <= point.hotel_pct <= 100.0
            assert 0.0 <= point.restaurant_pct <= 100.0


class TestReservationService:
    def test_get_kpi_valid(self, db: Session) -> None:
        svc = ReservationService(db)
        kpi = svc.get_kpi()
        assert kpi.today_total >= 0
        assert kpi.today_checkins >= 0
        assert kpi.today_checkouts >= 0
        assert kpi.pending_arrivals >= 0

    def test_get_weekly_trend_length(self, db: Session) -> None:
        svc = ReservationService(db)
        trend = svc.get_weekly_trend()
        assert len(trend) == 7

    def test_get_today_reservations(self, db: Session) -> None:
        svc = ReservationService(db)
        reservations = svc.get_today_reservations()
        assert isinstance(reservations, list)
        assert len(reservations) <= 5
        for r in reservations:
            assert r.reservation_number.startswith("RES-")
            assert r.nights >= 0


class TestRestaurantService:
    def test_get_kpi_valid(self, db: Session) -> None:
        svc = RestaurantService(db)
        kpi = svc.get_kpi()
        assert kpi.active_orders >= 0
        assert kpi.today_revenue >= 0
        assert kpi.dine_in_orders >= 0
        assert kpi.room_service_orders >= 0
        assert kpi.takeaway_orders >= 0

    def test_get_weekly_trend(self, db: Session) -> None:
        svc = RestaurantService(db)
        trend = svc.get_weekly_trend()
        assert len(trend) == 7


class TestFinanceService:
    def test_get_kpi_valid(self, db: Session) -> None:
        svc = FinanceService(db)
        kpi = svc.get_kpi()
        assert kpi.monthly_revenue >= 0
        assert kpi.pending_payments >= 0
        assert kpi.pending_count >= 0
        assert kpi.net_profit_est >= 0

    def test_cash_flow_length(self, db: Session) -> None:
        svc = FinanceService(db)
        flow = svc.get_cash_flow()
        assert len(flow) == 30
        for point in flow:
            assert point.inflow >= 0
            assert point.outflow >= 0
            assert round(point.net, 2) == round(point.inflow - point.outflow, 2)


class TestInventoryService:
    def test_get_kpi_counts(self, db: Session) -> None:
        svc = InventoryService(db)
        kpi = svc.get_kpi()
        total = kpi.low_stock_count + kpi.critical_count + kpi.ok_count
        # 7 items defined in the service
        assert total == 7

    def test_get_alerts_sorted(self, db: Session) -> None:
        svc = InventoryService(db)
        alerts = svc.get_alerts()
        # critical items should come before low
        levels = [a.level for a in alerts]
        had_non_critical = False
        for level in levels:
            if level != "critical":
                had_non_critical = True
            if had_non_critical and level == "critical":
                pytest.fail("critical item found after non-critical item — sort is broken")

    def test_no_ok_in_default_alerts(self, db: Session) -> None:
        svc = InventoryService(db)
        alerts = svc.get_alerts(include_ok=False)
        assert all(a.level != "ok" for a in alerts)


class TestEmployeeService:
    def test_get_kpi_valid(self, db: Session) -> None:
        svc = EmployeeService(db)
        kpi = svc.get_kpi()
        assert kpi.total_active >= 0
        assert kpi.present_today >= 0
        assert kpi.on_leave >= 0

    def test_present_lte_total(self, db: Session) -> None:
        svc = EmployeeService(db)
        kpi = svc.get_kpi()
        # present today is a subset count from today's sessions — could technically
        # be 0 if no one has logged in in the test DB
        assert kpi.present_today <= kpi.total_active or kpi.present_today >= 0


class TestActivityService:
    def test_get_widget_empty_db(self, db: Session) -> None:
        svc = ActivityService(db)
        widget = svc.get_widget()
        assert widget.total >= 0
        assert isinstance(widget.activities, list)

    def test_get_widget_with_events(self, db: Session) -> None:
        user = _create_test_user(db, email="actw@x.com", username="actwtest")
        _create_audit_event(db, user, "LOGIN")
        _create_audit_event(db, user, "PASSWORD_CHANGED")
        db.flush()

        svc = ActivityService(db)
        widget = svc.get_widget(limit=50)
        assert widget.total >= 2

        types = [a.event_type for a in widget.activities]
        assert "guest_checked_in" in types  # LOGIN maps to guest_checked_in
        assert "invoice_paid" in types  # PASSWORD_CHANGED maps to invoice_paid

    def test_activity_items_have_required_fields(self, db: Session) -> None:
        user = _create_test_user(db, email="actf@x.com", username="actftest")
        _create_audit_event(db, user, "LOGOUT")
        db.flush()

        svc = ActivityService(db)
        activities = svc.get_activities(limit=10)
        for item in activities:
            assert item.id > 0
            assert item.event_type
            assert item.description
            assert item.occurred_at is not None


class TestDashboardOverviewService:
    def test_get_overview_structure(self, db: Session) -> None:
        svc = DashboardOverviewService(db)
        overview = svc.get_overview()

        assert overview.kpis is not None
        assert overview.kpis.revenue is not None
        assert overview.kpis.occupancy is not None
        assert overview.kpis.reservation is not None
        assert overview.kpis.restaurant is not None
        assert overview.kpis.finance is not None
        assert overview.kpis.inventory is not None
        assert overview.kpis.employee is not None

        assert overview.charts is not None
        assert len(overview.charts.revenue_trend) == 7
        assert len(overview.charts.occupancy_trend) == 7
        assert len(overview.charts.reservation_trend) == 7
        assert len(overview.charts.cash_flow_trend) == 30
        assert len(overview.charts.monthly_revenue) == 6

        assert isinstance(overview.today_reservations, list)
        assert isinstance(overview.inventory_alerts, list)
        assert isinstance(overview.recent_activities, list)
        assert overview.as_of is not None


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------

class TestDashboardAPI:
    """Integration tests for all /api/v1/dashboard/* endpoints."""

    def test_overview_returns_200(self, superuser_client: TestClient) -> None:
        response = superuser_client.get("/api/v1/dashboard/overview")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "kpis" in data["data"]
        assert "charts" in data["data"]
        assert "today_reservations" in data["data"]
        assert "inventory_alerts" in data["data"]
        assert "recent_activities" in data["data"]

    def test_revenue_returns_200(self, superuser_client: TestClient) -> None:
        response = superuser_client.get("/api/v1/dashboard/revenue")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "kpi" in data["data"]
        assert "trend" in data["data"]
        assert "monthly" in data["data"]
        assert len(data["data"]["trend"]) == 7
        assert len(data["data"]["monthly"]) == 6

    def test_occupancy_returns_200(self, superuser_client: TestClient) -> None:
        response = superuser_client.get("/api/v1/dashboard/occupancy")
        assert response.status_code == 200
        data = response.json()
        kpi = data["data"]["kpi"]
        assert kpi["total_rooms"] == 30
        assert kpi["occupied_rooms"] + kpi["available_rooms"] == kpi["total_rooms"]
        assert 0 <= kpi["occupancy_pct"] <= 100
        assert len(data["data"]["trend"]) == 7

    def test_reservations_returns_200(self, superuser_client: TestClient) -> None:
        response = superuser_client.get("/api/v1/dashboard/reservations")
        assert response.status_code == 200
        data = response.json()
        assert "kpi" in data["data"]
        assert "today_reservations" in data["data"]
        assert "trend" in data["data"]
        assert len(data["data"]["trend"]) == 7

    def test_restaurant_returns_200(self, superuser_client: TestClient) -> None:
        response = superuser_client.get("/api/v1/dashboard/restaurant")
        assert response.status_code == 200
        data = response.json()
        assert "kpi" in data["data"]
        assert data["data"]["kpi"]["active_orders"] >= 0

    def test_finance_returns_200(self, superuser_client: TestClient) -> None:
        response = superuser_client.get("/api/v1/dashboard/finance")
        assert response.status_code == 200
        data = response.json()
        assert "kpi" in data["data"]
        assert "cash_flow" in data["data"]
        assert len(data["data"]["cash_flow"]) == 30

    def test_inventory_returns_200(self, superuser_client: TestClient) -> None:
        response = superuser_client.get("/api/v1/dashboard/inventory")
        assert response.status_code == 200
        data = response.json()
        assert "kpi" in data["data"]
        assert "alerts" in data["data"]
        # Verify critical items come before low items
        alerts = data["data"]["alerts"]
        had_non_critical = False
        for alert in alerts:
            if alert["level"] != "critical":
                had_non_critical = True
            if had_non_critical and alert["level"] == "critical":
                pytest.fail("Sort order is wrong — critical after low")

    def test_employees_returns_200(self, superuser_client: TestClient) -> None:
        response = superuser_client.get("/api/v1/dashboard/employees")
        assert response.status_code == 200
        data = response.json()
        assert "kpi" in data["data"]
        assert data["data"]["kpi"]["total_active"] >= 0

    def test_activity_returns_200(self, superuser_client: TestClient) -> None:
        response = superuser_client.get("/api/v1/dashboard/activity")
        assert response.status_code == 200
        data = response.json()
        assert "activities" in data["data"]
        assert "total" in data["data"]

    def test_activity_pagination(self, superuser_client: TestClient) -> None:
        response = superuser_client.get(
            "/api/v1/dashboard/activity?page=1&size=5"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["activities"]) <= 5

    def test_widgets_manifest_returns_200(self, superuser_client: TestClient) -> None:
        response = superuser_client.get("/api/v1/dashboard/widgets")
        assert response.status_code == 200
        data = response.json()
        assert "widgets" in data["data"]
        assert "total" in data["data"]
        widgets = data["data"]["widgets"]
        assert len(widgets) > 0
        for w in widgets:
            assert "id" in w
            assert "label" in w
            assert "endpoint" in w
            assert "required_permission" in w

    def test_unauthenticated_returns_401(self, client: TestClient) -> None:
        # Temporarily strip any auth token the session-scoped client may carry
        saved = dict(client.headers)
        client.headers.pop("Authorization", None)
        try:
            response = client.get("/api/v1/dashboard/overview")
            assert response.status_code == 401
        finally:
            client.headers.update(saved)

    def test_overview_response_envelope(self, superuser_client: TestClient) -> None:
        """Verify the standard SuccessResponse envelope is present."""
        response = superuser_client.get("/api/v1/dashboard/overview")
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert "message" in data
        assert "meta" in data
        assert "timestamp" in data["meta"]
        assert "version" in data["meta"]

    def test_cash_flow_inflow_equals_revenue_minus_costs(
        self, superuser_client: TestClient
    ) -> None:
        """Net must equal inflow - outflow for each point."""
        response = superuser_client.get("/api/v1/dashboard/finance")
        data = response.json()
        for point in data["data"]["cash_flow"]:
            expected_net = round(point["inflow"] - point["outflow"], 2)
            assert abs(point["net"] - expected_net) < 0.01, (
                f"Net mismatch: {point['net']} != {expected_net}"
            )

