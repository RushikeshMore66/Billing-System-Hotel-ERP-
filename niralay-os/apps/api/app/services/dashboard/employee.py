"""
Employee widget service for NiralayOS Dashboard.

Uses real User and Session data to compute employee presence metrics.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import EmployeeWidget, KPIEmployee


class EmployeeService:
    """Business logic for the Employee widget."""

    def __init__(self, db: Session) -> None:
        self._repo = DashboardRepository(db)

    def get_widget(self) -> EmployeeWidget:
        kpi = self.get_kpi()
        return EmployeeWidget(kpi=kpi)

    def get_kpi(self) -> KPIEmployee:
        total = self._repo.count_active_users()
        present = self._repo.count_users_logged_in_today()
        status_breakdown = self._repo.get_user_status_breakdown()

        # Users with 'inactive' or 'suspended' status count as on-leave proxy
        on_leave = status_breakdown.get("inactive", 0) + status_breakdown.get("suspended", 0)

        return KPIEmployee(
            total_active=total,
            present_today=present,
            on_leave=on_leave,
        )
