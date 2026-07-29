"""
Reservation Service.
"""
from typing import Optional, Sequence
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.reservation import Reservation, ReservationStatusHistory
from app.repositories.reservation import ReservationRepository
from app.schemas.reservation import ReservationCreate, ReservationUpdate
from app.core.constants import ReservationStatus
import random
import string
from datetime import datetime, timezone

class ReservationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ReservationRepository(db)

    def _generate_reservation_number(self) -> str:
        prefix = "RES"
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{prefix}-{suffix}"

    def get_reservation(self, reservation_id: int) -> Reservation:
        reservation = self.repo.get_by_id(reservation_id)
        if not reservation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
        return reservation
        
    def get_reservation_by_number(self, reservation_number: str) -> Reservation:
        reservation = self.repo.get_by_number(reservation_number)
        if not reservation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
        return reservation

    def search_reservations(self, query: Optional[str] = None, status_filter: Optional[ReservationStatus] = None, skip: int = 0, limit: int = 20) -> tuple[Sequence[Reservation], int]:
        return self.repo.search(query=query, status=status_filter, skip=skip, limit=limit)

    def create_reservation(self, data: ReservationCreate, current_user_name: str = "System") -> Reservation:
        reservation = Reservation(**data.model_dump())
        reservation.reservation_number = self._generate_reservation_number()
        
        if not reservation.nights:
            reservation.nights = (reservation.check_out_date - reservation.check_in_date).days
            if reservation.nights <= 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Check-out date must be after check-in date")
                
        reservation = self.repo.create(reservation)
        
        history = ReservationStatusHistory(
            reservation_id=reservation.id,
            to_status=reservation.status,
            changed_by=current_user_name,
            changed_at=datetime.now(timezone.utc)
        )
        self.repo.add_status_history(history)
        
        return reservation

    def update_reservation(self, reservation_id: int, data: ReservationUpdate, current_user_name: str = "System") -> Reservation:
        reservation = self.get_reservation(reservation_id)
        update_data = data.model_dump(exclude_unset=True)
        
        old_status = reservation.status
        
        for key, value in update_data.items():
            setattr(reservation, key, value)
            
        reservation = self.repo.save(reservation)
        
        if "status" in update_data and old_status != update_data["status"]:
            history = ReservationStatusHistory(
                reservation_id=reservation.id,
                from_status=old_status,
                to_status=reservation.status,
                changed_by=current_user_name,
                changed_at=datetime.now(timezone.utc)
            )
            self.repo.add_status_history(history)
            
        return reservation
