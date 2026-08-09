"""
Expense repository for NiralayOS.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional, Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.expense import Expense, ExpenseCategory
from app.repositories.base import BaseRepository


class ExpenseCategoryRepository(BaseRepository[ExpenseCategory]):
    def __init__(self, db: Session) -> None:
        super().__init__(ExpenseCategory, db)

    def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        stmt = select(self.model).where(
            func.lower(self.model.name) == name.lower(),
            self.model.is_active.is_(True),
        )
        if exclude_id:
            stmt = stmt.where(self.model.id != exclude_id)
        return self.db.scalars(stmt).first() is not None

    def list_all(self, active_only: bool = True) -> Sequence[ExpenseCategory]:
        stmt = select(self.model).order_by(self.model.display_order, self.model.name)
        if active_only:
            stmt = stmt.where(self.model.is_active.is_(True))
        return self.db.scalars(stmt).all()


class ExpenseRepository(BaseRepository[Expense]):
    def __init__(self, db: Session) -> None:
        super().__init__(Expense, db)

    def search(
        self,
        query: Optional[str] = None,
        category_id: Optional[int] = None,
        payment_method: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[Expense], int]:
        stmt = select(self.model)

        if active_only:
            stmt = stmt.where(self.model.is_active.is_(True))

        if query:
            stmt = stmt.where(
                or_(
                    self.model.description.ilike(f"%{query}%"),
                    self.model.vendor_name.ilike(f"%{query}%"),
                    self.model.reference_number.ilike(f"%{query}%"),
                )
            )

        if category_id is not None:
            stmt = stmt.where(self.model.category_id == category_id)

        if payment_method:
            stmt = stmt.where(self.model.payment_method == payment_method)

        if date_from:
            stmt = stmt.where(self.model.expense_date >= date_from)

        if date_to:
            stmt = stmt.where(self.model.expense_date <= date_to)

        stmt = stmt.order_by(self.model.expense_date.desc(), self.model.id.desc())

        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        stmt = stmt.offset(skip).limit(limit)
        return self.db.scalars(stmt).all(), total

    def get_monthly_totals(
        self,
        year: int,
        month: int,
    ) -> dict:
        """Get total expenses for a given month."""
        from sqlalchemy import extract
        stmt = select(
            func.sum(self.model.amount).label("total_amount"),
            func.sum(self.model.tax_amount).label("total_tax"),
            func.count(self.model.id).label("count"),
        ).where(
            self.model.is_active.is_(True),
            extract("year", self.model.expense_date) == year,
            extract("month", self.model.expense_date) == month,
        )
        row = self.db.execute(stmt).first()
        return {
            "total_amount": row.total_amount or Decimal("0"),
            "total_tax": row.total_tax or Decimal("0"),
            "count": row.count or 0,
        }
