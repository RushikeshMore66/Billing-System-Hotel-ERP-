"""
Guest Service.
"""
from typing import Optional, Sequence
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.guest import Guest
from app.repositories.guest import GuestRepository
from app.schemas.guest import GuestCreate, GuestUpdate

class GuestService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = GuestRepository(db)

    def get_guest(self, guest_id: int) -> Guest:
        guest = self.repo.get_by_id(guest_id)
        if not guest:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found")
        return guest

    def search_guests(self, query: Optional[str] = None, skip: int = 0, limit: int = 20) -> tuple[Sequence[Guest], int]:
        return self.repo.search(query=query, skip=skip, limit=limit)

    def create_guest(self, data: GuestCreate) -> Guest:
        guest = Guest(**data.model_dump())
        return self.repo.create(guest)

    def update_guest(self, guest_id: int, data: GuestUpdate) -> Guest:
        guest = self.get_guest(guest_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(guest, key, value)
        return self.repo.save(guest)
