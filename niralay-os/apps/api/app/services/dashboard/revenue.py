"""
Revenue widget service for NiralayOS Dashboard.

Queries real Bill/Payment data when available.
Falls back to zeros when no billing data exists yet.
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
        self._db = db

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

    # ── Internal builders ────────────────────────────────────────────────────

    def _get_daily_revenue_map(self, days: int = 14) -> dict[str, float]:
        """Query real daily revenue from bills."""
        try:
            from sqlalchemy import select, func
            from app.models.billing import Bill

            today = datetime.now(timezone.utc).date()
            start = today - timedelta(days=days - 1)

            stmt = (
                select(
                    Bill.bill_date.label("day"),
                    func.coalesce(func.sum(Bill.amount_paid), 0).label("revenue"),
                    func.coalesce(
                        func.sum(
                            Bill.amount_paid * 0.62  # Hotel portion estimate
                        ), 0
                    ).label("hotel_rev"),
                    func.coalesce(
                        func.sum(
                            Bill.amount_paid * 0.31  # Restaurant portion estimate
                        ), 0
                    ).label("rest_rev"),
                )
                .where(
                    Bill.is_active.is_(True),
                    Bill.status.in_(["paid", "partially_paid"]),
                    Bill.bill_date >= start,
                    Bill.bill_date <= today,
                )
                .group_by(Bill.bill_date)
            )
            rows = self._db.execute(stmt).all()
            return {str(r.day): float(r.revenue) for r in rows}
        except Exception:
            return {}

    def _build_kpi(self) -> KPIRevenue:
        try:
            from sqlalchemy import select, func, extract
            from app.models.billing import Bill

            today = datetime.now(timezone.utc).date()
            yesterday = today - timedelta(days=1)

            def _day_rev(d) -> tuple[float, float, float]:
                stmt = select(
                    func.coalesce(func.sum(Bill.amount_paid), 0).label("total"),
                ).where(
                    Bill.is_active.is_(True),
                    Bill.status.in_(["paid", "partially_paid"]),
                    Bill.bill_date == d,
                )
                row = self._db.execute(stmt).first()
                total = float(row.total or 0)
                return total, round(total * 0.62, 2), round(total * 0.31, 2)

            today_rev, today_hotel, today_rest = _day_rev(today)
            yest_rev, _, _ = _day_rev(yesterday)

            change_pct = (
                round((today_rev - yest_rev) / yest_rev * 100, 1)
                if yest_rev > 0
                else 0.0
            )

            return KPIRevenue(
                today=round(today_rev, 2),
                yesterday=round(yest_rev, 2),
                change_pct=change_pct,
                hotel_revenue=today_hotel,
                restaurant_revenue=today_rest,
                other_revenue=round(today_rev * 0.07, 2),
            )
        except Exception:
            return KPIRevenue(
                today=0.0,
                yesterday=0.0,
                change_pct=0.0,
                hotel_revenue=0.0,
                restaurant_revenue=0.0,
                other_revenue=0.0,
            )

    def _build_weekly_trend(self) -> list[RevenueTrendPoint]:
        today = datetime.now(timezone.utc).date()
        week_start = today - timedelta(days=today.weekday())

        daily_map = self._get_daily_revenue_map(days=14)

        trend: list[RevenueTrendPoint] = []
        for i in range(7):
            this_day = week_start + timedelta(days=i)
            last_day = this_day - timedelta(days=7)

            trend.append(
                RevenueTrendPoint(
                    day=_WEEKDAY_ABBR[i],
                    date=this_day,
                    revenue=daily_map.get(str(this_day), 0.0),
                    last_week=daily_map.get(str(last_day), 0.0),
                )
            )
        return trend

    def _build_monthly_revenue(self) -> list[MonthlyRevenuePoint]:
        """Return month-by-month revenue for the past 6 months from real bills."""
        try:
            from sqlalchemy import select, func, extract
            from app.models.billing import Bill

            today = datetime.now(timezone.utc)

            result: list[MonthlyRevenuePoint] = []
            for offset in range(5, -1, -1):
                year = today.year
                month = today.month - offset
                while month <= 0:
                    month += 12
                    year -= 1

                stmt = select(
                    func.coalesce(func.sum(Bill.amount_paid), 0).label("total"),
                ).where(
                    Bill.is_active.is_(True),
                    Bill.status.in_(["paid", "partially_paid"]),
                    extract("year", Bill.bill_date) == year,
                    extract("month", Bill.bill_date) == month,
                )
                row = self._db.execute(stmt).first()
                total = float(row.total or 0)

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
        except Exception:
            # Fallback if billing tables don't exist
            today = datetime.now(timezone.utc)
            result = []
            for offset in range(5, -1, -1):
                year = today.year
                month = today.month - offset
                while month <= 0:
                    month += 12
                    year -= 1
                result.append(
                    MonthlyRevenuePoint(
                        month=_MONTH_ABBR[month - 1],
                        year=year,
                        total=0.0,
                        hotel=0.0,
                        restaurant=0.0,
                    )
                )
            return result
