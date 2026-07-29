"""
Guest Repository.
"""
from typing import Optional, Sequence
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session
from app.models.guest import Guest
from app.repositories.base import BaseRepository

class GuestRepository(BaseRepository[Guest]):
    def __init__(self, db: Session):
        super().__init__(Guest, db)

    def search(self, query: Optional[str] = None, skip: int = 0, limit: int = 20) -> tuple[Sequence[Guest], int]:
        stmt = select(self.model)
        
        if query:
            stmt = stmt.where(
                or_(
                    self.model.full_name.ilike(f"%{query}%"),
                    self.model.email.ilike(f"%{query}%"),
                    self.model.phone.ilike(f"%{query}%"),
                    self.model.id_number.ilike(f"%{query}%")
                )
            )
            
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        
        stmt = stmt.offset(skip).limit(limit)
        items = self.db.scalars(stmt).all()
        return items, total
