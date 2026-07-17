"""
Role and Permission service for NiralayOS.

Business logic for:
  - Creating and managing roles
  - Assigning/revoking permissions on roles
  - Assigning/revoking roles on users
  - Resolving a user's effective permission set
"""

from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.role import Role, Permission
from app.repositories.role import RoleRepository, PermissionRepository
from app.repositories.user import UserRepository
from app.schemas.role import RoleCreate, RoleUpdate, PermissionCreate


class PermissionService:
    def __init__(self, db: Session) -> None:
        self._repo = PermissionRepository(db)

    def create(self, data: PermissionCreate) -> Permission:
        if self._repo.code_exists(data.code):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Permission code '{data.code}' already exists.",
            )
        perm = Permission(
            code=data.code,
            module=data.module,
            action=data.action,
            description=data.description,
        )
        return self._repo.create(perm)

    def list(self, skip: int = 0, limit: int = 200) -> tuple[list[Permission], int]:
        return self._repo.list_active(skip=skip, limit=limit)

    def get_by_id(self, perm_id: int) -> Permission:
        perm = self._repo.get_by_id(perm_id)
        if not perm:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
        return perm


class RoleService:
    def __init__(self, db: Session) -> None:
        self._repo = RoleRepository(db)
        self._perm_repo = PermissionRepository(db)
        self._user_repo = UserRepository(db)

    def create(self, data: RoleCreate) -> Role:
        if self._repo.slug_exists(data.slug):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Role slug '{data.slug}' already exists.",
            )
        permissions = self._perm_repo.get_by_ids(data.permission_ids) if data.permission_ids else []
        role = Role(
            name=data.name,
            slug=data.slug,
            description=data.description,
            permissions=permissions,
        )
        return self._repo.create(role)

    def update(self, role_id: int, data: RoleUpdate) -> Role:
        role = self._get_or_404(role_id)
        if data.name is not None:
            role.name = data.name
        if data.description is not None:
            role.description = data.description
        if data.permission_ids is not None:
            role.permissions = self._perm_repo.get_by_ids(data.permission_ids)
        return self._repo.save(role)

    def assign_permissions(self, role_id: int, permission_ids: list[int]) -> Role:
        role = self._get_or_404(role_id)
        new_perms = self._perm_repo.get_by_ids(permission_ids)
        existing_ids = {p.id for p in role.permissions}
        for perm in new_perms:
            if perm.id not in existing_ids:
                role.permissions.append(perm)
        return self._repo.save(role)

    def revoke_permissions(self, role_id: int, permission_ids: list[int]) -> Role:
        role = self._get_or_404(role_id)
        revoke_set = set(permission_ids)
        role.permissions = [p for p in role.permissions if p.id not in revoke_set]
        return self._repo.save(role)

    def list(self, skip: int = 0, limit: int = 100) -> tuple[list[Role], int]:
        return self._repo.list_active(skip=skip, limit=limit)

    def get_by_id(self, role_id: int) -> Role:
        return self._get_or_404(role_id)

    def assign_role_to_user(self, user_id: int, role_id: int, assigned_by: Optional[str] = None) -> None:
        user = self._user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        role = self._get_or_404(role_id)
        if role not in user.roles:
            user.roles.append(role)
            self._user_repo.save(user)

    def revoke_role_from_user(self, user_id: int, role_id: int) -> None:
        user = self._user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        role = self._get_or_404(role_id)
        if role in user.roles:
            user.roles.remove(role)
            self._user_repo.save(user)

    def get_user_permissions(self, user_id: int) -> list[str]:
        user = self._user_repo.get_by_id(user_id)
        if not user:
            return []
        return user.permission_codes

    def _get_or_404(self, role_id: int) -> Role:
        role = self._repo.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        return role
