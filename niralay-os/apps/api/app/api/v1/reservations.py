"""
Reservations Router.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.schemas.reservation import ReservationCreate, ReservationUpdate, ReservationResponse
from app.schemas.base import SuccessResponse, PaginatedResponse
from app.services.reservation import ReservationService
from app.core.constants import ReservationStatus

router = APIRouter(prefix="/reservations", tags=["Reservations"])

@router.get("", response_model=PaginatedResponse[ReservationResponse])
def list_reservations(
    search: Optional[str] = None,
    status_filter: Optional[ReservationStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PaginatedResponse[ReservationResponse]:
    svc = ReservationService(db)
    skip = (page - 1) * size
    items, total = svc.search_reservations(query=search, status_filter=status_filter, skip=skip, limit=size)
    return PaginatedResponse.of(items=items, total=total, page=page, size=size)

@router.post("", response_model=SuccessResponse[ReservationResponse], status_code=status.HTTP_201_CREATED)
def create_reservation(
    data: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[ReservationResponse]:
    svc = ReservationService(db)
    reservation = svc.create_reservation(data, current_user_name=current_user.full_name)
    return SuccessResponse.of(data=reservation, message="Reservation created successfully")

@router.get("/{reservation_id}", response_model=SuccessResponse[ReservationResponse])
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[ReservationResponse]:
    svc = ReservationService(db)
    reservation = svc.get_reservation(reservation_id)
    return SuccessResponse.of(data=reservation)

@router.patch("/{reservation_id}", response_model=SuccessResponse[ReservationResponse])
def update_reservation(
    reservation_id: int,
    data: ReservationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[ReservationResponse]:
    svc = ReservationService(db)
    reservation = svc.update_reservation(reservation_id, data, current_user_name=current_user.full_name)
    return SuccessResponse.of(data=reservation, message="Reservation updated successfully")
