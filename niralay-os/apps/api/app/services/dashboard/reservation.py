"""
Reservation widget service for NiralayOS Dashboard.

Data source: audit_logs LOGIN events are used as a proxy.
Replace with Reservation model queries once Sprint 3 is complete.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import (
    DashboardReservation,
    KPIReservation,
    ReservationTrendPoint,
    ReservationWidget,
)

_WEEKDAY_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class ReservationService:
    """Business logic for the Reservation widget."""

    def __init__(self, db: Session) -> None:
        self._repo = DashboardRepository(db)

    def get_widget(self) -> ReservationWidget:
        kpi = self.get_kpi()
        today_res = self.get_today_reservations()
        trend = self.get_weekly_trend()
        return ReservationWidget(kpi=kpi, today_reservations=today_res, trend=trend)

    def get_kpi(self) -> KPIReservation:
        """
        Derive reservation-like counts from today's audit events.

        Mappings:
          - LOGIN success → today check-in equivalent
          - LOGOUT        → today check-out equivalent
          - USER_CREATED  → new reservation equivalent
        """
        today = self._repo.get_audit_counts_today()

        checkins = today.get("LOGIN", 0)
        checkouts = today.get("LOGOUT", 0)
        new_res = today.get("USER_CREATED", 0)
        total = checkins + new_res

        return KPIReservation(
            today_total=total,
            today_checkins=checkins,
            today_checkouts=checkouts,
            pending_arrivals=max(total - checkins, 0),
        )

    def get_today_reservations(self) -> list[DashboardReservation]:
        """
        Return today's reservation-like records derived from audit logs.

        In Sprint 3 this will be replaced with a direct Reservation model query.
        """
        activities = self._repo.get_recent_activities(limit=10)
        reservations: list[DashboardReservation] = []
        today = datetime.now(timezone.utc).date()

        for idx, row in enumerate(activities):
            event = row.get("event", "")
            if event not in ("LOGIN", "USER_CREATED", "LOGOUT"):
                continue

            status_map = {
                "LOGIN": "checked-in",
                "USER_CREATED": "confirmed",
                "LOGOUT": "checkout",
            }

            occurred: datetime = row["created_at"]
            if occurred.tzinfo is None:
                occurred = occurred.replace(tzinfo=timezone.utc)

            checkout_date = today + timedelta(days=2)

            reservations.append(
                DashboardReservation(
                    id=row["id"],
                    reservation_number=f"RES-{1000 + row['id']:04d}",
                    guest_name=row.get("actor_name") or "System Event",
                    room_number=None,
                    room_type=None,
                    check_in=today,
                    check_out=checkout_date,
                    nights=2,
                    amount=8_000.0,
                    status=status_map.get(event, "pending"),
                    source="Direct",
                    created_at=occurred,
                )
            )

        return reservations[:5]  # dashboard shows top 5

    def get_weekly_trend(self) -> list[ReservationTrendPoint]:
        """Return 7-day reservation trend."""
        today = datetime.now(timezone.utc).date()
        week_start = today - timedelta(days=today.weekday())

        login_by_day = {
            str(r["day"]): r["count"]
            for r in self._repo.get_event_counts_by_day("LOGIN", days=7)
        }
        logout_by_day = {
            str(r["day"]): r["count"]
            for r in self._repo.get_event_counts_by_day("LOGOUT", days=7)
        }
        created_by_day = {
            str(r["day"]): r["count"]
            for r in self._repo.get_event_counts_by_day("USER_CREATED", days=7)
        }

        trend: list[ReservationTrendPoint] = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            key = str(day)
            trend.append(
                ReservationTrendPoint(
                    date=day,
                    new_reservations=created_by_day.get(key, 0),
                    check_ins=login_by_day.get(key, 0),
                    check_outs=logout_by_day.get(key, 0),
                )
            )
        return trend
