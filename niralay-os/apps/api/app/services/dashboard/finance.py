"""
Finance widget service for NiralayOS Dashboard.

Computes pending payments, monthly revenue and net profit estimate.
Replace with Bill/Payment model queries in Sprint 3.
"""

from __future__ import annotations

from datetime import timedelta, timezone, datetime

from sqlalchemy.orm import Session

from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import (
    CashFlowPoint,
    FinanceWidget,
    KPIFinance,
)

_COGS_RATIO = 0.68  # hospitality industry standard cost ratio


class FinanceService:
    """Business logic for the Finance widget."""

    def __init__(self, db: Session) -> None:
        self._repo = DashboardRepository(db)

    def get_widget(self) -> FinanceWidget:
        kpi = self.get_kpi()
        cash_flow = self.get_cash_flow()
        return FinanceWidget(kpi=kpi, cash_flow=cash_flow)

    def get_kpi(self) -> KPIFinance:
        monthly = self._repo.get_monthly_login_summary(months=1)
        month_count = sum(r["count"] for r in monthly)
        monthly_rev = month_count * 8_000.0

        # Pending payments proxy: 15% of monthly revenue unpaid on average
        pending_amount = round(monthly_rev * 0.15, 2)
        pending_count = max(int(month_count * 0.10), 0)

        net_profit = round(monthly_rev * (1.0 - _COGS_RATIO), 2)

        return KPIFinance(
            pending_payments=pending_amount,
            pending_count=pending_count,
            monthly_revenue=round(monthly_rev, 2),
            net_profit_est=net_profit,
        )

    def get_cash_flow(self) -> list[CashFlowPoint]:
        """
        Return 30-day cash flow (inflow = revenue, outflow = estimated costs).
        """
        today = datetime.now(timezone.utc).date()
        daily_counts = self._repo.get_daily_login_counts(days=30)
        counts_by_date = {str(r["day"]): r["count"] for r in daily_counts}

        result: list[CashFlowPoint] = []
        for offset in range(29, -1, -1):
            day = today - timedelta(days=offset)
            count = counts_by_date.get(str(day), 0)
            inflow = count * 8_000.0
            outflow = round(inflow * _COGS_RATIO, 2)
            result.append(
                CashFlowPoint(
                    date=day,
                    inflow=round(inflow, 2),
                    outflow=outflow,
                    net=round(inflow - outflow, 2),
                )
            )
        return result
