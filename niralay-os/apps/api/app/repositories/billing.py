"""
Billing repository for NiralayOS.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional, Sequence

from sqlalchemy import extract, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.billing import Bill, BillItem, Payment
from app.repositories.base import BaseRepository


class BillRepository(BaseRepository[Bill]):
    def __init__(self, db: Session) -> None:
        super().__init__(Bill, db)

    def get_with_details(self, bill_id: int) -> Optional[Bill]:
        """Load bill with items and payments in one query."""
        stmt = (
            select(self.model)
            .options(
                joinedload(self.model.items),
                joinedload(self.model.payments),
            )
            .where(self.model.id == bill_id)
        )
        return self.db.scalars(stmt).first()

    def get_by_number(self, bill_number: str) -> Optional[Bill]:
        stmt = select(self.model).where(self.model.bill_number == bill_number)
        return self.db.scalars(stmt).first()

    def number_exists(self, bill_number: str) -> bool:
        return self.get_by_number(bill_number) is not None

    def search(
        self,
        query: Optional[str] = None,
        status: Optional[str] = None,
        bill_type: Optional[str] = None,
        reservation_id: Optional[int] = None,
        guest_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[Bill], int]:
        stmt = select(self.model)

        if active_only:
            stmt = stmt.where(self.model.is_active.is_(True))

        if query:
            stmt = stmt.where(
                or_(
                    self.model.bill_number.ilike(f"%{query}%"),
                    self.model.table_number.ilike(f"%{query}%"),
                )
            )

        if status:
            stmt = stmt.where(self.model.status == status)

        if bill_type:
            stmt = stmt.where(self.model.bill_type == bill_type)

        if reservation_id is not None:
            stmt = stmt.where(self.model.reservation_id == reservation_id)

        if guest_id is not None:
            stmt = stmt.where(self.model.guest_id == guest_id)

        if date_from:
            stmt = stmt.where(self.model.bill_date >= date_from)

        if date_to:
            stmt = stmt.where(self.model.bill_date <= date_to)

        stmt = stmt.order_by(self.model.bill_date.desc(), self.model.id.desc())

        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        stmt = stmt.offset(skip).limit(limit)
        return self.db.scalars(stmt).all(), total

    def get_monthly_revenue(self, year: int, month: int) -> dict:
        """Revenue from paid/partially-paid bills for a given month."""
        stmt = select(
            func.sum(self.model.amount_paid).label("total_paid"),
            func.sum(self.model.total_amount).label("total_billed"),
            func.count(self.model.id).label("count"),
        ).where(
            self.model.is_active.is_(True),
            self.model.status.in_(["paid", "partially_paid"]),
            extract("year", self.model.bill_date) == year,
            extract("month", self.model.bill_date) == month,
        )
        row = self.db.execute(stmt).first()
        return {
            "total_paid": row.total_paid or Decimal("0"),
            "total_billed": row.total_billed or Decimal("0"),
            "count": row.count or 0,
        }

    def get_pending_payments_summary(self) -> dict:
        """Outstanding bills summary."""
        stmt = select(
            func.sum(self.model.amount_due).label("total_due"),
            func.count(self.model.id).label("count"),
        ).where(
            self.model.is_active.is_(True),
            self.model.status.in_(["issued", "partially_paid"]),
            self.model.amount_due > 0,
        )
        row = self.db.execute(stmt).first()
        return {
            "total_due": row.total_due or Decimal("0"),
            "count": row.count or 0,
        }

    def get_daily_revenue(self, days: int = 30) -> list[dict]:
        """Day-by-day revenue totals for the last N days."""
        from datetime import datetime, timezone, timedelta
        end_date = datetime.now(timezone.utc).date()
        start_date = end_date - timedelta(days=days - 1)

        stmt = (
            select(
                self.model.bill_date.label("day"),
                func.sum(self.model.amount_paid).label("revenue"),
                func.count(self.model.id).label("count"),
            )
            .where(
                self.model.is_active.is_(True),
                self.model.status.in_(["paid", "partially_paid"]),
                self.model.bill_date >= start_date,
                self.model.bill_date <= end_date,
            )
            .group_by(self.model.bill_date)
            .order_by(self.model.bill_date)
        )
        rows = self.db.execute(stmt).all()
        return [{"day": r.day, "revenue": r.revenue or Decimal("0"), "count": r.count} for r in rows]


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, db: Session) -> None:
        super().__init__(Payment, db)

    def get_bill_payments(self, bill_id: int) -> Sequence[Payment]:
        stmt = (
            select(self.model)
            .where(self.model.bill_id == bill_id, self.model.status == "success")
            .order_by(self.model.payment_date.desc())
        )
        return self.db.scalars(stmt).all()
