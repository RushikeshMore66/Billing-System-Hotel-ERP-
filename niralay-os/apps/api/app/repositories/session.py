"""
Session and RefreshToken repositories for NiralayOS.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.session import Session, RefreshToken
from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository[Session]):
    def __init__(self, db: DBSession) -> None:
        super().__init__(Session, db)

    def get_by_jti(self, jti: str) -> Optional[Session]:
        return self.db.query(Session).filter(Session.jti == jti).first()

    def list_active_for_user(self, user_id: int) -> list[Session]:
        now = datetime.now(timezone.utc)
        return (
            self.db.query(Session)
            .filter(
                Session.user_id == user_id,
                Session.is_revoked.is_(False),
                Session.logout_at.is_(None),
                Session.expires_at > now,
            )
            .order_by(Session.login_at.desc())
            .all()
        )

    def revoke(self, session: Session) -> None:
        session.is_revoked = True
        session.logout_at = datetime.now(timezone.utc)
        self.db.flush()

    def revoke_all_for_user(self, user_id: int) -> int:
        now = datetime.now(timezone.utc)
        updated = (
            self.db.query(Session)
            .filter(
                Session.user_id == user_id,
                Session.is_revoked.is_(False),
            )
            .update({"is_revoked": True, "logout_at": now}, synchronize_session=False)
        )
        self.db.flush()
        return updated  # type: ignore[return-value]

    def touch_activity(self, session: Session) -> None:
        session.last_activity_at = datetime.now(timezone.utc)
        self.db.flush()


class RefreshTokenRepository:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def get_by_jti(self, jti: str) -> Optional[RefreshToken]:
        return self.db.query(RefreshToken).filter(RefreshToken.jti == jti).first()

    def get_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        return self.db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    def create(self, rt: RefreshToken) -> RefreshToken:
        self.db.add(rt)
        self.db.flush()
        self.db.refresh(rt)
        return rt

    def revoke(self, rt: RefreshToken) -> None:
        rt.is_revoked = True
        rt.revoked_at = datetime.now(timezone.utc)
        self.db.flush()

    def revoke_all_for_session(self, session_id: int) -> None:
        now = datetime.now(timezone.utc)
        self.db.query(RefreshToken).filter(
            RefreshToken.session_id == session_id,
            RefreshToken.is_revoked.is_(False),
        ).update({"is_revoked": True, "revoked_at": now}, synchronize_session=False)
        self.db.flush()


class AuditLogRepository:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def append(self, log: object) -> None:
        """Append-only insert — never update audit logs."""
        self.db.add(log)
        self.db.flush()

    def list_recent(self, skip: int = 0, limit: int = 50) -> list[object]:
        from app.models.audit_log import AuditLog
        return (
            self.db.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
