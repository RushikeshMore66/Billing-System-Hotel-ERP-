"""
Billing Router for NiralayOS.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.schemas.base import PaginatedResponse, SuccessResponse
from app.schemas.billing import (
    BillCreate,
    BillItemCreate,
    BillOut,
    BillSummary,
    BillUpdate,
    PaymentCreate,
    PaymentOut,
)
from app.services.billing import BillingService

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.get("/bills", response_model=PaginatedResponse[BillSummary])
def list_bills(
    search: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    bill_type: Optional[str] = None,
    reservation_id: Optional[int] = None,
    guest_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PaginatedResponse[BillSummary]:
    svc = BillingService(db)
    skip = (page - 1) * size
    bills, total = svc.search(
        query=search,
        status_filter=status_filter,
        bill_type=bill_type,
        reservation_id=reservation_id,
        guest_id=guest_id,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=size,
    )
    return PaginatedResponse.of(items=bills, total=total, page=page, size=size)


@router.post(
    "/bills",
    response_model=SuccessResponse[BillOut],
    status_code=status.HTTP_201_CREATED,
)
def create_bill(
    data: BillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[BillOut]:
    svc = BillingService(db)
    bill = svc.create(data, current_user=str(current_user.uuid))
    return SuccessResponse.of(data=bill, message="Bill created successfully")


@router.get("/bills/{bill_id}", response_model=SuccessResponse[BillOut])
def get_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[BillOut]:
    svc = BillingService(db)
    return SuccessResponse.of(data=svc.get(bill_id))


@router.patch("/bills/{bill_id}", response_model=SuccessResponse[BillOut])
def update_bill(
    bill_id: int,
    data: BillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[BillOut]:
    svc = BillingService(db)
    return SuccessResponse.of(data=svc.update(bill_id, data), message="Bill updated")


@router.post("/bills/{bill_id}/items", response_model=SuccessResponse[BillOut])
def add_items(
    bill_id: int,
    items: list[BillItemCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[BillOut]:
    svc = BillingService(db)
    bill = svc.add_items(bill_id, items)
    return SuccessResponse.of(data=bill, message="Items added to bill")


@router.post("/bills/{bill_id}/issue", response_model=SuccessResponse[BillOut])
def issue_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[BillOut]:
    svc = BillingService(db)
    return SuccessResponse.of(data=svc.issue_bill(bill_id), message="Bill issued")


@router.post(
    "/bills/{bill_id}/payments",
    response_model=SuccessResponse[PaymentOut],
    status_code=status.HTTP_201_CREATED,
)
def record_payment(
    bill_id: int,
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[PaymentOut]:
    svc = BillingService(db)
    payment = svc.record_payment(bill_id, data, received_by=current_user.full_name)
    return SuccessResponse.of(data=payment, message="Payment recorded successfully")


@router.post("/bills/{bill_id}/void", response_model=SuccessResponse[BillOut])
def void_bill(
    bill_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[BillOut]:
    svc = BillingService(db)
    return SuccessResponse.of(
        data=svc.void_bill(bill_id, reason, voided_by=str(current_user.uuid)),
        message="Bill voided",
    )
