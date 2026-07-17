"""
Role and Permission repositories for NiralayOS.
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.role import Role, Permission
from app.repositories.base import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    def __init__(self, db: Session) -> None:
        super().__init__(Permission, db)

    def get_by_code(self, code: str) -> Optional[Permission]:
        return self.db.query(Permission).filter(Permission.code == code).first()

    def get_by_codes(self, codes: list[str]) -> list[Permission]:
        return self.db.query(Permission).filter(Permission.code.in_(codes)).all()

    def get_by_module(self, module: str) -> list[Permission]:
        return self.db.query(Permission).filter(Permission.module == module).all()

    def list_active(self, skip: int = 0, limit: int = 200) -> tuple[list[Permission], int]:
        q = self.db.query(Permission).filter(Permission.is_active.is_(True))
        total = q.count()
        items = q.order_by(Permission.module, Permission.action).offset(skip).limit(limit).all()
        return items, total

    def get_by_ids(self, ids: list[int]) -> list[Permission]:
        return self.db.query(Permission).filter(Permission.id.in_(ids)).all()

    def code_exists(self, code: str) -> bool:
        return self.db.query(Permission.id).filter(Permission.code == code).first() is not None


class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: Session) -> None:
        super().__init__(Role, db)

    def get_by_name(self, name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.name == name).first()

    def get_by_slug(self, slug: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.slug == slug).first()

    def get_by_uuid(self, role_uuid: UUID | str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.uuid == role_uuid).first()

    def get_by_ids(self, ids: list[int]) -> list[Role]:
        return self.db.query(Role).filter(Role.id.in_(ids)).all()

    def list_active(self, skip: int = 0, limit: int = 100) -> tuple[list[Role], int]:
        q = self.db.query(Role).filter(Role.is_active.is_(True))
        total = q.count()
        items = q.order_by(Role.name).offset(skip).limit(limit).all()
        return items, total

    def slug_exists(self, slug: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(Role.id).filter(Role.slug == slug)
        if exclude_id:
            q = q.filter(Role.id != exclude_id)
        return q.first() is not None
