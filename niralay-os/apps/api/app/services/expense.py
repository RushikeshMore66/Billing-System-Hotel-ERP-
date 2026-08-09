"""
Expense service for NiralayOS.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.expense import Expense, ExpenseCategory
from app.repositories.expense import ExpenseCategoryRepository, ExpenseRepository
from app.schemas.expense import ExpenseCategoryCreate, ExpenseCategoryUpdate, ExpenseCreate, ExpenseUpdate


class ExpenseCategoryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ExpenseCategoryRepository(db)

    def list_all(self) -> Sequence[ExpenseCategory]:
        return self.repo.list_all()

    def get(self, category_id: int) -> ExpenseCategory:
        cat = self.repo.get_by_id(category_id)
        if not cat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense category not found")
        return cat

    def create(self, data: ExpenseCategoryCreate) -> ExpenseCategory:
        if self.repo.name_exists(data.name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category '{data.name}' already exists",
            )
        cat = ExpenseCategory(**data.model_dump())
        return self.repo.create(cat)

    def update(self, category_id: int, data: ExpenseCategoryUpdate) -> ExpenseCategory:
        cat = self.get(category_id)
        update_data = data.model_dump(exclude_unset=True)
        if "name" in update_data and self.repo.name_exists(update_data["name"], exclude_id=category_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category '{update_data['name']}' already exists",
            )
        for key, value in update_data.items():
            setattr(cat, key, value)
        return self.repo.save(cat)

    def delete(self, category_id: int) -> None:
        cat = self.get(category_id)
        if getattr(cat, "is_system", False):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete a system expense category",
            )
        cat.soft_delete()
        self.repo.save(cat)


class ExpenseService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ExpenseRepository(db)

    def get(self, expense_id: int) -> Expense:
        exp = self.repo.get_by_id(expense_id)
        if not exp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        return exp

    def search(
        self,
        query: Optional[str] = None,
        category_id: Optional[int] = None,
        payment_method: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[Expense], int]:
        return self.repo.search(
            query=query,
            category_id=category_id,
            payment_method=payment_method,
            date_from=date_from,
            date_to=date_to,
            skip=skip,
            limit=limit,
        )

    def create(self, data: ExpenseCreate) -> Expense:
        amount = data.amount
        tax_amount = data.tax_amount
        total_amount = amount + tax_amount

        expense = Expense(
            category_id=data.category_id,
            description=data.description,
            amount=amount,
            tax_amount=tax_amount,
            total_amount=total_amount,
            expense_date=data.expense_date,
            payment_method=data.payment_method,
            vendor_name=data.vendor_name,
            vendor_contact=data.vendor_contact,
            reference_number=data.reference_number,
            notes=data.notes,
        )
        return self.repo.create(expense)

    def update(self, expense_id: int, data: ExpenseUpdate) -> Expense:
        expense = self.get(expense_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(expense, key, value)
        # Recompute total_amount if amount or tax changed
        expense.total_amount = expense.amount + expense.tax_amount
        return self.repo.save(expense)

    def delete(self, expense_id: int) -> None:
        expense = self.get(expense_id)
        expense.soft_delete()
        self.repo.save(expense)

    def get_monthly_totals(self, year: int, month: int) -> dict:
        return self.repo.get_monthly_totals(year=year, month=month)
