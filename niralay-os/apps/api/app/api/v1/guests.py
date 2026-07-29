"""
Guests Router.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.schemas.guest import GuestCreate, GuestUpdate, GuestResponse
from app.schemas.base import SuccessResponse, PaginatedResponse
from app.services.guest import GuestService

router = APIRouter(prefix="/guests", tags=["Guests"])

@router.get("", response_model=PaginatedResponse[GuestResponse])
def list_guests(
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PaginatedResponse[GuestResponse]:
    svc = GuestService(db)
    skip = (page - 1) * size
    items, total = svc.search_guests(query=search, skip=skip, limit=size)
    return PaginatedResponse.of(items=items, total=total, page=page, size=size)

@router.post("", response_model=SuccessResponse[GuestResponse], status_code=status.HTTP_201_CREATED)
def create_guest(
    data: GuestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[GuestResponse]:
    svc = GuestService(db)
    guest = svc.create_guest(data)
    return SuccessResponse.of(data=guest, message="Guest created successfully")

@router.get("/{guest_id}", response_model=SuccessResponse[GuestResponse])
def get_guest(
    guest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[GuestResponse]:
    svc = GuestService(db)
    guest = svc.get_guest(guest_id)
    return SuccessResponse.of(data=guest)

@router.patch("/{guest_id}", response_model=SuccessResponse[GuestResponse])
def update_guest(
    guest_id: int,
    data: GuestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[GuestResponse]:
    svc = GuestService(db)
    guest = svc.update_guest(guest_id, data)
    return SuccessResponse.of(data=guest, message="Guest updated successfully")
