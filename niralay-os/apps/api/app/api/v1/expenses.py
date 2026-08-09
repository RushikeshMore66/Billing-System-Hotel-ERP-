"""
Expenses Router for NiralayOS.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.schemas.base import PaginatedResponse, SuccessResponse
from app.schemas.expense import (
    ExpenseCategoryCreate,
    ExpenseCategoryOut,
    ExpenseCategoryUpdate,
    ExpenseCreate,
    ExpenseOut,
    ExpenseUpdate,
)
from app.services.expense import ExpenseCategoryService, ExpenseService

router = APIRouter(prefix="/expenses", tags=["Expenses"])


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------
@router.get("/categories", response_model=SuccessResponse[list[ExpenseCategoryOut]])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[list[ExpenseCategoryOut]]:
    svc = ExpenseCategoryService(db)
    return SuccessResponse.of(data=svc.list_all())


@router.post(
    "/categories",
    response_model=SuccessResponse[ExpenseCategoryOut],
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    data: ExpenseCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[ExpenseCategoryOut]:
    svc = ExpenseCategoryService(db)
    return SuccessResponse.of(data=svc.create(data), message="Category created")


@router.patch("/categories/{category_id}", response_model=SuccessResponse[ExpenseCategoryOut])
def update_category(
    category_id: int,
    data: ExpenseCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[ExpenseCategoryOut]:
    svc = ExpenseCategoryService(db)
    return SuccessResponse.of(data=svc.update(category_id, data), message="Category updated")


@router.delete("/categories/{category_id}", response_model=SuccessResponse[None])
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[None]:
    svc = ExpenseCategoryService(db)
    svc.delete(category_id)
    return SuccessResponse.of(data=None, message="Category deleted")


# ---------------------------------------------------------------------------
# Expenses
# ---------------------------------------------------------------------------
@router.get("", response_model=PaginatedResponse[ExpenseOut])
def list_expenses(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    payment_method: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PaginatedResponse[ExpenseOut]:
    svc = ExpenseService(db)
    skip = (page - 1) * size
    items, total = svc.search(
        query=search,
        category_id=category_id,
        payment_method=payment_method,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=size,
    )
    return PaginatedResponse.of(items=items, total=total, page=page, size=size)


@router.post(
    "",
    response_model=SuccessResponse[ExpenseOut],
    status_code=status.HTTP_201_CREATED,
)
def create_expense(
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[ExpenseOut]:
    svc = ExpenseService(db)
    return SuccessResponse.of(data=svc.create(data), message="Expense created successfully")


@router.get("/{expense_id}", response_model=SuccessResponse[ExpenseOut])
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[ExpenseOut]:
    svc = ExpenseService(db)
    return SuccessResponse.of(data=svc.get(expense_id))


@router.patch("/{expense_id}", response_model=SuccessResponse[ExpenseOut])
def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[ExpenseOut]:
    svc = ExpenseService(db)
    return SuccessResponse.of(data=svc.update(expense_id, data), message="Expense updated")


@router.delete("/{expense_id}", response_model=SuccessResponse[None])
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[None]:
    svc = ExpenseService(db)
    svc.delete(expense_id)
    return SuccessResponse.of(data=None, message="Expense deleted")
