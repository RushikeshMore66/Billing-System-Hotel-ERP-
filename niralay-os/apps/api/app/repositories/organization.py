"""
Organisation configuration repositories for NiralayOS.

Pure database I/O — no business logic.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.organization import Department, Designation, GuestIDType
from app.repositories.base import BaseRepository


# ---------------------------------------------------------------------------
# Department
# ---------------------------------------------------------------------------
class DepartmentRepository(BaseRepository[Department]):
    def __init__(self, db: Session) -> None:
        super().__init__(Department, db)

    def list_active(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> tuple[list[Department], int]:
        q = self.db.query(Department).filter(Department.is_active.is_(True))
        if search:
            q = q.filter(Department.name.ilike(f"%{search}%"))
        total = q.count()
        items = q.order_by(Department.display_order, Department.name).offset(skip).limit(limit).all()
        return items, total

    def code_exists(self, code: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(Department.id).filter(Department.code == code)
        if exclude_id:
            q = q.filter(Department.id != exclude_id)
        return q.first() is not None

    def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(Department.id).filter(Department.name == name)
        if exclude_id:
            q = q.filter(Department.id != exclude_id)
        return q.first() is not None


# ---------------------------------------------------------------------------
# Designation
# ---------------------------------------------------------------------------
class DesignationRepository(BaseRepository[Designation]):
    def __init__(self, db: Session) -> None:
        super().__init__(Designation, db)

    def list_active(
        self,
        skip: int = 0,
        limit: int = 200,
        search: Optional[str] = None,
        department_id: Optional[int] = None,
    ) -> tuple[list[Designation], int]:
        q = self.db.query(Designation).filter(Designation.is_active.is_(True))
        if search:
            q = q.filter(Designation.name.ilike(f"%{search}%"))
        if department_id is not None:
            q = q.filter(Designation.department_id == department_id)
        total = q.count()
        items = q.order_by(Designation.display_order, Designation.name).offset(skip).limit(limit).all()
        return items, total

    def code_exists(self, code: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(Designation.id).filter(Designation.code == code)
        if exclude_id:
            q = q.filter(Designation.id != exclude_id)
        return q.first() is not None


# ---------------------------------------------------------------------------
# GuestIDType
# ---------------------------------------------------------------------------
class GuestIDTypeRepository(BaseRepository[GuestIDType]):
    def __init__(self, db: Session) -> None:
        super().__init__(GuestIDType, db)

    def list_active(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> tuple[list[GuestIDType], int]:
        q = self.db.query(GuestIDType).filter(GuestIDType.is_active.is_(True))
        if search:
            q = q.filter(GuestIDType.name.ilike(f"%{search}%"))
        total = q.count()
        items = q.order_by(GuestIDType.display_order, GuestIDType.name).offset(skip).limit(limit).all()
        return items, total

    def code_exists(self, code: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(GuestIDType.id).filter(GuestIDType.code == code)
        if exclude_id:
            q = q.filter(GuestIDType.id != exclude_id)
        return q.first() is not None

    def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(GuestIDType.id).filter(GuestIDType.name == name)
        if exclude_id:
            q = q.filter(GuestIDType.id != exclude_id)
        return q.first() is not None
