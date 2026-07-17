"""
Revenue widget service for NiralayOS Dashboard.

Computes revenue KPIs and trend data.

Data sources (current):
  - audit_logs LOGIN events are used as an activity proxy.
  - Real revenue figures will be sourced from bills/payments in Sprint 3.

All monetary amounts are in INR (paise-free float).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import (
    KPIRevenue,
    MonthlyRevenuePoint,
    RevenueTrendPoint,
    RevenueWidget,
)

_WEEKDAY_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_MONTH_ABBR = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


class RevenueService:
    """Business logic for the Revenue widget."""

    def __init__(self, db: Session) -> None:
        self._repo = DashboardRepository(db)

    def get_widget(self) -> RevenueWidget:
        kpi = self._build_kpi()
        trend = self._build_weekly_trend()
        monthly = self._build_monthly_revenue()
        return RevenueWidget(kpi=kpi, trend=trend, monthly=monthly)

    def get_kpi(self) -> KPIRevenue:
        return self._build_kpi()

    def get_weekly_trend(self) -> list[RevenueTrendPoint]:
        return self._build_weekly_trend()

    def get_monthly_revenue(self) -> list[MonthlyRevenuePoint]:
        return self._build_monthly_revenue()

    # ----------------------------------------------------------------
    # Internal builders
    # ----------------------------------------------------------------
    def _build_kpi(self) -> KPIRevenue:
        """
        Build revenue KPIs.

        Since billing tables are not yet seeded, we derive a synthetic
        revenue figure from user-session activity counts scaled by a
        reasonable average revenue-per-active-session estimate.

        Replace the _compute_revenue_from_activity calls with real
        billing queries once Sprint 3 (Billing) is complete.
        """
        today_count = self._repo.get_audit_counts_today()
        yesterday_count = self._repo.get_audit_counts_yesterday()

        today_logins = today_count.get("LOGIN", 0)
        yesterday_logins = yesterday_count.get("LOGIN", 0)

        # Realistic hotel revenue estimation (₹8,000 avg/booking equivalent)
        AVG_REVENUE_PER_EVENT = 8_000.0
        today_rev = today_logins * AVG_REVENUE_PER_EVENT
        yesterday_rev = yesterday_logins * AVG_REVENUE_PER_EVENT

        # Split across revenue streams (typical hotel ratios)
        hotel_pct = 0.62
        restaurant_pct = 0.31
        other_pct = 0.07

        change_pct = (
            round((today_rev - yesterday_rev) / yesterday_rev * 100, 1)
            if yesterday_rev > 0
            else 0.0
        )

        return KPIRevenue(
            today=round(today_rev, 2),
            yesterday=round(yesterday_rev, 2),
            change_pct=change_pct,
            hotel_revenue=round(today_rev * hotel_pct, 2),
            restaurant_revenue=round(today_rev * restaurant_pct, 2),
            other_revenue=round(today_rev * other_pct, 2),
        )

    def _build_weekly_trend(self) -> list[RevenueTrendPoint]:
        """
        Return 7-day revenue trend (this week vs last week).
        """
        today = datetime.now(timezone.utc).date()
        # Start from Monday of the current week
        week_start = today - timedelta(days=today.weekday())

        # Fetch login counts for last 14 days
        daily_counts = self._repo.get_daily_login_counts(days=14)
        counts_by_date: dict[str, int] = {
            str(row["day"]): row["count"] for row in daily_counts
        }

        trend: list[RevenueTrendPoint] = []
        for i in range(7):
            this_day = week_start + timedelta(days=i)
            last_day = this_day - timedelta(days=7)

            this_count = counts_by_date.get(str(this_day), 0)
            last_count = counts_by_date.get(str(last_day), 0)

            AVG = 8_000.0
            trend.append(
                RevenueTrendPoint(
                    day=_WEEKDAY_ABBR[i],
                    date=this_day,
                    revenue=round(this_count * AVG, 2),
                    last_week=round(last_count * AVG, 2),
                )
            )
        return trend

    def _build_monthly_revenue(self) -> list[MonthlyRevenuePoint]:
        """Return month-by-month revenue for the past 6 months."""
        monthly_data = self._repo.get_monthly_login_summary(months=6)
        counts_by_ym: dict[tuple[int, int], int] = {
            (row["year"], row["month"]): row["count"] for row in monthly_data
        }

        today = datetime.now(timezone.utc)
        result: list[MonthlyRevenuePoint] = []
        for offset in range(5, -1, -1):
            # Go back `offset` months from today
            year = today.year
            month = today.month - offset
            while month <= 0:
                month += 12
                year -= 1

            count = counts_by_ym.get((year, month), 0)
            total = count * 8_000.0
            result.append(
                MonthlyRevenuePoint(
                    month=_MONTH_ABBR[month - 1],
                    year=year,
                    total=round(total, 2),
                    hotel=round(total * 0.62, 2),
                    restaurant=round(total * 0.31, 2),
                )
            )
        return result
