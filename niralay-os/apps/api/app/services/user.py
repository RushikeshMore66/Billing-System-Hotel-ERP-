"""
User service for NiralayOS.

Business logic for user lifecycle management:
  - Creating users with password policy enforcement
  - Updating user fields
  - Soft-deleting / deactivating users
  - Password history checks
"""

from __future__ import annotations

import re
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.core.settings import get_settings
from app.models.user import User
from app.repositories.user import (
    UserRepository,
    PasswordHistoryRepository,
    UserPreferenceRepository,
)
from app.repositories.role import RoleRepository
from app.schemas.user import UserCreate, UserUpdate

_PASSWORD_RE = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{12,}$"
)


class UserService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = UserRepository(db)
        self._pw_history = PasswordHistoryRepository(db)
        self._prefs = UserPreferenceRepository(db)
        self._roles = RoleRepository(db)
        self._cfg = get_settings()

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------
    def create(self, data: UserCreate, created_by: Optional[str] = None) -> User:
        self._assert_password_policy(data.password)
        if self._repo.email_exists(data.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")
        if self._repo.username_exists(data.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken.")

        pw_hash = hash_password(data.password)
        roles = self._roles.get_by_ids(data.role_ids) if data.role_ids else []

        user = User(
            username=data.username,
            email=data.email.lower(),
            phone=data.phone,
            password_hash=pw_hash,
            full_name=data.full_name,
            department=data.department,
            designation=data.designation,
            is_superuser=data.is_superuser,
            created_by=created_by,
            roles=roles,
        )
        self._repo.create(user)

        # Seed password history and default preferences
        self._pw_history.add_hash(user.id, pw_hash)
        self._prefs.create_default(user.id)

        return user

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def get_by_id(self, user_id: int) -> User:
        user = self._repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return user

    def list(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> tuple[list[User], int]:
        return self._repo.list_active(skip=skip, limit=limit, search=search)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update(self, user_id: int, data: UserUpdate, updated_by: Optional[str] = None) -> User:
        user = self.get_by_id(user_id)

        if data.email is not None:
            if self._repo.email_exists(data.email, exclude_id=user_id):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")
            user.email = data.email.lower()

        for field in ("phone", "full_name", "avatar", "department", "designation", "status"):
            val = getattr(data, field, None)
            if val is not None:
                setattr(user, field, val)

        if data.role_ids is not None:
            user.roles = self._roles.get_by_ids(data.role_ids)

        user.updated_by = updated_by
        return self._repo.save(user)

    # ------------------------------------------------------------------
    # Delete (soft)
    # ------------------------------------------------------------------
    def deactivate(self, user_id: int, deleted_by: Optional[str] = None) -> None:
        user = self.get_by_id(user_id)
        user.soft_delete(deleted_by=deleted_by)
        self._repo.save(user)

    # ------------------------------------------------------------------
    # Password management (called by AuthService)
    # ------------------------------------------------------------------
    def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> None:
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )
        self._set_new_password(user, new_password)

    def set_password_after_reset(self, user: User, new_password: str) -> None:
        self._set_new_password(user, new_password)

    def _set_new_password(self, user: User, new_password: str) -> None:
        self._assert_password_policy(new_password)
        self._assert_not_reused(user.id, new_password)
        pw_hash = hash_password(new_password)
        user.password_hash = pw_hash
        user.password_reset_token = None
        user.password_reset_expires = None
        self._repo.save(user)
        # Record in history and prune
        self._pw_history.add_hash(user.id, pw_hash)
        self._pw_history.prune_old(user.id, self._cfg.PASSWORD_HISTORY_COUNT + 1)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _assert_password_policy(self, password: str) -> None:
        cfg = self._cfg
        if len(password) < cfg.PASSWORD_MIN_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Password must be at least {cfg.PASSWORD_MIN_LENGTH} characters.",
            )
        if not _PASSWORD_RE.match(password):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must contain uppercase, lowercase, digit, and special character.",
            )

    def _assert_not_reused(self, user_id: int, new_password: str) -> None:
        count = self._cfg.PASSWORD_HISTORY_COUNT
        if count <= 0:
            return
        recent_hashes = self._pw_history.get_recent_hashes(user_id, count)
        for old_hash in recent_hashes:
            if verify_password(new_password, old_hash):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Cannot reuse any of your last {count} passwords.",
                )
