"""
User repository for NiralayOS.

Only database I/O — no business logic.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.user import User, PasswordHistory, UserPreference
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session) -> None:
        super().__init__(User, db)

    # ------------------------------------------------------------------
    # Lookups
    # ------------------------------------------------------------------
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email.lower()).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_uuid(self, user_uuid: UUID | str) -> Optional[User]:
        return self.db.query(User).filter(User.uuid == user_uuid).first()

    def get_by_reset_token(self, token: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(
                User.password_reset_token == token,
                User.password_reset_expires > datetime.now(timezone.utc),
            )
            .first()
        )

    def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(User.id).filter(User.email == email.lower())
        if exclude_id:
            q = q.filter(User.id != exclude_id)
        return q.first() is not None

    def username_exists(self, username: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(User.id).filter(User.username == username)
        if exclude_id:
            q = q.filter(User.id != exclude_id)
        return q.first() is not None

    # ------------------------------------------------------------------
    # List / paginate
    # ------------------------------------------------------------------
    def list_active(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> tuple[list[User], int]:
        q = self.db.query(User).filter(User.is_active.is_(True))
        if search:
            term = f"%{search}%"
            q = q.filter(
                or_(
                    User.full_name.ilike(term),
                    User.email.ilike(term),
                    User.username.ilike(term),
                )
            )
        total = q.count()
        items = q.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    # ------------------------------------------------------------------
    # Lockout
    # ------------------------------------------------------------------
    def increment_failed_login(self, user: User) -> None:
        user.failed_login_count += 1
        self.db.flush()

    def reset_failed_login(self, user: User) -> None:
        user.failed_login_count = 0
        user.locked_until = None
        self.db.flush()

    def lock_account(self, user: User, until: datetime) -> None:
        user.locked_until = until
        self.db.flush()


class PasswordHistoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_recent_hashes(self, user_id: int, count: int) -> list[str]:
        rows = (
            self.db.query(PasswordHistory.password_hash)
            .filter(PasswordHistory.user_id == user_id)
            .order_by(PasswordHistory.created_at.desc())
            .limit(count)
            .all()
        )
        return [r[0] for r in rows]

    def add_hash(self, user_id: int, password_hash: str) -> None:
        entry = PasswordHistory(user_id=user_id, password_hash=password_hash)
        self.db.add(entry)
        self.db.flush()

    def prune_old(self, user_id: int, keep: int) -> None:
        """Keep only the `keep` most recent records for this user."""
        keep_ids = (
            self.db.query(PasswordHistory.id)
            .filter(PasswordHistory.user_id == user_id)
            .order_by(PasswordHistory.created_at.desc())
            .limit(keep)
            .all()
        )
        keep_id_list = [r[0] for r in keep_ids]
        self.db.query(PasswordHistory).filter(
            PasswordHistory.user_id == user_id,
            PasswordHistory.id.notin_(keep_id_list),
        ).delete(synchronize_session=False)
        self.db.flush()


class UserPreferenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_user(self, user_id: int) -> Optional[UserPreference]:
        return self.db.query(UserPreference).filter(UserPreference.user_id == user_id).first()

    def create_default(self, user_id: int) -> UserPreference:
        pref = UserPreference(user_id=user_id)
        self.db.add(pref)
        self.db.flush()
        return pref
