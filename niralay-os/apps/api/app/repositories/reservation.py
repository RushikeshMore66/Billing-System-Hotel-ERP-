"""
Reservation Repository.
"""
from typing import Optional, Sequence
from sqlalchemy import select, or_, func, desc
from sqlalchemy.orm import Session, joinedload
from app.models.reservation import Reservation, ReservationStatusHistory
from app.models.guest import Guest
from app.repositories.base import BaseRepository
from app.core.constants import ReservationStatus

class ReservationRepository(BaseRepository[Reservation]):
    def __init__(self, db: Session):
        super().__init__(Reservation, db)

    def get_by_number(self, reservation_number: str) -> Optional[Reservation]:
        stmt = select(self.model).options(joinedload(self.model.guest)).where(self.model.reservation_number == reservation_number)
        return self.db.scalars(stmt).first()

    def add_status_history(self, history: ReservationStatusHistory) -> ReservationStatusHistory:
        self.db.add(history)
        self.db.flush()
        return history

    def search(
        self, 
        query: Optional[str] = None, 
        status: Optional[ReservationStatus] = None, 
        skip: int = 0, 
        limit: int = 20
    ) -> tuple[Sequence[Reservation], int]:
        stmt = select(self.model).join(self.model.guest).options(joinedload(self.model.guest))
        
        if query:
            stmt = stmt.where(
                or_(
                    self.model.reservation_number.ilike(f"%{query}%"),
                    Guest.full_name.ilike(f"%{query}%"),
                    Guest.email.ilike(f"%{query}%"),
                    Guest.phone.ilike(f"%{query}%")
                )
            )
            
        if status:
            stmt = stmt.where(self.model.status == status)
            
        stmt = stmt.order_by(desc(self.model.created_at))
            
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        
        stmt = stmt.offset(skip).limit(limit)
        items = self.db.scalars(stmt).all()
        return items, total
