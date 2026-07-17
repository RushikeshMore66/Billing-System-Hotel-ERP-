"""
Occupancy widget service for NiralayOS Dashboard.

Computes hotel and restaurant occupancy metrics.

Data sources:
  - UserSession.is_revoked / logout_at / expires_at → active guest sessions
  - User.status → employee/guest counts

Real occupancy data will come from Room/Reservation tables in Sprint 3.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import (
    KPIOccupancy,
    OccupancyTrendPoint,
    OccupancyWidget,
)

# Representative hotel configuration — move to Settings in Sprint 3
_DEFAULT_TOTAL_ROOMS = 30
_DEFAULT_RESTAURANT_CAPACITY = 80  # covers (seats)


class OccupancyService:
    """Business logic for the Occupancy widget."""

    def __init__(self, db: Session) -> None:
        self._repo = DashboardRepository(db)

    def get_widget(self) -> OccupancyWidget:
        kpi = self.get_kpi()
        trend = self.get_hourly_trend()
        return OccupancyWidget(kpi=kpi, trend=trend)

    def get_kpi(self) -> KPIOccupancy:
        """
        Compute occupancy KPI.

        Active sessions count as a proxy for current checked-in guests
        until Room/Reservation tables are available.
        """
        active_sessions = self._repo.count_active_sessions()

        # Treat sessions as guest occupancy (each session = 1 checked-in guest)
        occupied = min(active_sessions, _DEFAULT_TOTAL_ROOMS)
        available = max(_DEFAULT_TOTAL_ROOMS - occupied, 0)
        pct = round(occupied / _DEFAULT_TOTAL_ROOMS * 100, 1)

        return KPIOccupancy(
            total_rooms=_DEFAULT_TOTAL_ROOMS,
            occupied_rooms=occupied,
            available_rooms=available,
            occupancy_pct=pct,
            current_guests=active_sessions,
        )

    def get_hourly_trend(self) -> list[OccupancyTrendPoint]:
        """
        Return a 7-point intra-day occupancy trend (6am to 12am).

        Hotel occupancy is derived from the current occupancy pct with a
        realistic hourly distribution curve typical for Indian hotels.
        Restaurant occupancy follows meal-service peaks.
        """
        kpi = self.get_kpi()
        base_hotel_pct = kpi.occupancy_pct

        # Hourly multipliers relative to base (reflects typical check-in/out patterns)
        hotel_curve = [0.60, 0.80, 0.92, 0.92, 1.00, 1.00, 0.97]
        restaurant_curve = [0.12, 0.50, 1.00, 0.65, 0.85, 1.00, 0.35]

        hours = ["6am", "9am", "12pm", "3pm", "6pm", "9pm", "12am"]

        return [
            OccupancyTrendPoint(
                hour=hours[i],
                hotel_pct=round(min(base_hotel_pct * hotel_curve[i], 100.0), 1),
                restaurant_pct=round(restaurant_curve[i] * 100.0, 1),
            )
            for i in range(7)
        ]
