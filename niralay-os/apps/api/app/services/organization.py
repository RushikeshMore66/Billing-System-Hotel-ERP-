"""
Organisation configuration service for NiralayOS.

Business validation:
  - Duplicate department codes/names
  - Designation must belong to valid department
"""

from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.organization import Department, Designation, GuestIDType
from app.repositories.organization import (
    DepartmentRepository,
    DesignationRepository,
    GuestIDTypeRepository,
)
from app.schemas.organization import (
    DepartmentCreate,
    DepartmentUpdate,
    DesignationCreate,
    DesignationUpdate,
    GuestIDTypeCreate,
    GuestIDTypeUpdate,
)


class DepartmentService:
    def __init__(self, db: Session) -> None:
        self._repo = DepartmentRepository(db)

    def list(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> tuple[list[Department], int]:
        return self._repo.list_active(skip=skip, limit=limit, search=search)

    def get_by_id(self, dept_id: int) -> Department:
        d = self._repo.get_by_id(dept_id)
        if not d or not d.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found.")
        return d

    def create(self, data: DepartmentCreate, created_by: Optional[str] = None) -> Department:
        if self._repo.code_exists(data.code):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Department code '{data.code}' already exists.")
        if self._repo.name_exists(data.name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Department name '{data.name}' already exists.")
        d = Department(**data.model_dump(), created_by=created_by)
        return self._repo.create(d)

    def update(self, dept_id: int, data: DepartmentUpdate, updated_by: Optional[str] = None) -> Department:
        d = self.get_by_id(dept_id)
        if data.name is not None and data.name != d.name:
            if self._repo.name_exists(data.name, exclude_id=dept_id):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Department name already exists.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(d, field, value)
        d.updated_by = updated_by
        return self._repo.save(d)

    def delete(self, dept_id: int, deleted_by: Optional[str] = None) -> None:
        d = self.get_by_id(dept_id)
        if d.is_system:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="System departments cannot be deleted.")
        d.soft_delete(deleted_by=deleted_by)
        self._repo.save(d)


class DesignationService:
    def __init__(self, db: Session) -> None:
        self._repo = DesignationRepository(db)
        self._dept_repo = DepartmentRepository(db)

    def list(
        self,
        skip: int = 0,
        limit: int = 200,
        search: Optional[str] = None,
        department_id: Optional[int] = None,
    ) -> tuple[list[Designation], int]:
        return self._repo.list_active(skip=skip, limit=limit, search=search, department_id=department_id)

    def get_by_id(self, desig_id: int) -> Designation:
        d = self._repo.get_by_id(desig_id)
        if not d or not d.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Designation not found.")
        return d

    def create(self, data: DesignationCreate, created_by: Optional[str] = None) -> Designation:
        if self._repo.code_exists(data.code):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Designation code '{data.code}' already exists.")
        if data.department_id is not None:
            dept = self._dept_repo.get_by_id(data.department_id)
            if not dept or not dept.is_active:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found.")
        d = Designation(**data.model_dump(), created_by=created_by)
        return self._repo.create(d)

    def update(self, desig_id: int, data: DesignationUpdate, updated_by: Optional[str] = None) -> Designation:
        d = self.get_by_id(desig_id)
        if data.department_id is not None:
            dept = self._dept_repo.get_by_id(data.department_id)
            if not dept or not dept.is_active:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(d, field, value)
        d.updated_by = updated_by
        return self._repo.save(d)

    def delete(self, desig_id: int, deleted_by: Optional[str] = None) -> None:
        d = self.get_by_id(desig_id)
        if d.is_system:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="System designations cannot be deleted.")
        d.soft_delete(deleted_by=deleted_by)
        self._repo.save(d)


class GuestIDTypeService:
    def __init__(self, db: Session) -> None:
        self._repo = GuestIDTypeRepository(db)

    def list(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> tuple[list[GuestIDType], int]:
        return self._repo.list_active(skip=skip, limit=limit, search=search)

    def get_by_id(self, id_type_id: int) -> GuestIDType:
        g = self._repo.get_by_id(id_type_id)
        if not g or not g.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest ID type not found.")
        return g

    def create(self, data: GuestIDTypeCreate, created_by: Optional[str] = None) -> GuestIDType:
        if self._repo.code_exists(data.code):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"ID type code '{data.code}' already exists.")
        if self._repo.name_exists(data.name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"ID type name '{data.name}' already exists.")
        g = GuestIDType(**data.model_dump(), created_by=created_by)
        return self._repo.create(g)

    def update(self, id_type_id: int, data: GuestIDTypeUpdate, updated_by: Optional[str] = None) -> GuestIDType:
        g = self.get_by_id(id_type_id)
        if data.name is not None and data.name != g.name:
            if self._repo.name_exists(data.name, exclude_id=id_type_id):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="ID type name already exists.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(g, field, value)
        g.updated_by = updated_by
        return self._repo.save(g)

    def delete(self, id_type_id: int, deleted_by: Optional[str] = None) -> None:
        g = self.get_by_id(id_type_id)
        if g.is_system:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="System ID types cannot be deleted.")
        g.soft_delete(deleted_by=deleted_by)
        self._repo.save(g)
