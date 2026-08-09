"""
Finance widget service for NiralayOS Dashboard.

Queries real Bill/Payment data when available.
Falls back to zero values when no billing data exists yet.
"""

from __future__ import annotations

from datetime import date, timedelta, timezone, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import (
    CashFlowPoint,
    FinanceWidget,
    KPIFinance,
)


class FinanceService:
    """Business logic for the Finance widget."""

    def __init__(self, db: Session) -> None:
        self._repo = DashboardRepository(db)
        self._db = db

    def get_widget(self) -> FinanceWidget:
        kpi = self.get_kpi()
        cash_flow = self.get_cash_flow()
        return FinanceWidget(kpi=kpi, cash_flow=cash_flow)

    def get_kpi(self) -> KPIFinance:
        try:
            from sqlalchemy import select, func, extract
            from app.models.billing import Bill, Payment

            now = datetime.now(timezone.utc)
            year, month = now.year, now.month

            # Monthly revenue from paid bills
            monthly_stmt = select(
                func.coalesce(func.sum(Bill.amount_paid), 0).label("total_paid"),
            ).where(
                Bill.is_active.is_(True),
                Bill.status.in_(["paid", "partially_paid"]),
                extract("year", Bill.bill_date) == year,
                extract("month", Bill.bill_date) == month,
            )
            monthly_row = self._db.execute(monthly_stmt).first()
            monthly_rev = float(monthly_row.total_paid or 0)

            # Pending payments (outstanding bills)
            pending_stmt = select(
                func.coalesce(func.sum(Bill.amount_due), 0).label("total_due"),
                func.count(Bill.id).label("count"),
            ).where(
                Bill.is_active.is_(True),
                Bill.status.in_(["issued", "partially_paid"]),
                Bill.amount_due > 0,
            )
            pending_row = self._db.execute(pending_stmt).first()
            pending_amount = float(pending_row.total_due or 0)
            pending_count = int(pending_row.count or 0)

            # Net profit estimate (using industry COGS ratio of 68%)
            _COGS_RATIO = 0.68
            net_profit = round(monthly_rev * (1.0 - _COGS_RATIO), 2)

            return KPIFinance(
                pending_payments=round(pending_amount, 2),
                pending_count=pending_count,
                monthly_revenue=round(monthly_rev, 2),
                net_profit_est=net_profit,
            )
        except Exception:
            # Billing tables may not exist in test/initial environment
            return KPIFinance(
                pending_payments=0.0,
                pending_count=0,
                monthly_revenue=0.0,
                net_profit_est=0.0,
            )

    def get_cash_flow(self) -> list[CashFlowPoint]:
        """Return 30-day cash flow from real Bill/Payment data."""
        try:
            from sqlalchemy import select, func, and_
            from app.models.billing import Bill

            today = datetime.now(timezone.utc).date()
            start = today - timedelta(days=29)

            # Daily revenue from paid bills
            stmt = (
                select(
                    Bill.bill_date.label("day"),
                    func.coalesce(func.sum(Bill.amount_paid), 0).label("inflow"),
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
            inflow_by_date = {str(r.day): float(r.inflow) for r in rows}

            # Try to get expenses too
            try:
                from app.models.expense import Expense
                exp_stmt = (
                    select(
                        Expense.expense_date.label("day"),
                        func.coalesce(func.sum(Expense.total_amount), 0).label("outflow"),
                    )
                    .where(
                        Expense.is_active.is_(True),
                        Expense.expense_date >= start,
                        Expense.expense_date <= today,
                    )
                    .group_by(Expense.expense_date)
                )
                exp_rows = self._db.execute(exp_stmt).all()
                outflow_by_date = {str(r.day): float(r.outflow) for r in exp_rows}
            except Exception:
                outflow_by_date = {}

            _COGS_RATIO = 0.68
            result: list[CashFlowPoint] = []
            for offset in range(29, -1, -1):
                day = today - timedelta(days=offset)
                day_str = str(day)
                inflow = inflow_by_date.get(day_str, 0.0)
                # Use real expense data if available, else estimate
                outflow = outflow_by_date.get(day_str, round(inflow * _COGS_RATIO, 2))
                result.append(
                    CashFlowPoint(
                        date=day,
                        inflow=round(inflow, 2),
                        outflow=round(outflow, 2),
                        net=round(inflow - outflow, 2),
                    )
                )
            return result
        except Exception:
            # Fallback: return 30 days of zeros
            today = datetime.now(timezone.utc).date()
            return [
                CashFlowPoint(
                    date=today - timedelta(days=i),
                    inflow=0.0,
                    outflow=0.0,
                    net=0.0,
                )
                for i in range(29, -1, -1)
            ]
