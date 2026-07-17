"""
Authentication service for NiralayOS.

Business logic for:
  - Login (credential validation, lockout, session creation, token issuance)
  - Logout (session revocation, token revocation)
  - Token refresh (rotation — old revoked, new issued)
  - Password change and forgot/reset flow
  - Account lockout enforcement
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.settings import get_settings
from app.models.session import Session as UserSession, RefreshToken
from app.models.user import User
from app.repositories.session import (
    SessionRepository,
    RefreshTokenRepository,
    AuditLogRepository,
)
from app.repositories.user import UserRepository, PasswordHistoryRepository
from app.schemas.auth import TokenResponse
from app.services.audit import AuditService


def _hash_token(raw: str) -> str:
    """SHA-256 hash used to store refresh tokens without exposing the raw value."""
    return hashlib.sha256(raw.encode()).hexdigest()


class AuthService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._cfg = get_settings()
        self._user_repo = UserRepository(db)
        self._session_repo = SessionRepository(db)
        self._rt_repo = RefreshTokenRepository(db)
        self._pw_history = PasswordHistoryRepository(db)
        self._audit = AuditService(db)

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------
    def login(
        self,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        user = self._user_repo.get_by_email(email)

        if not user or not user.is_active:
            self._audit.log(
                "LOGIN_FAILED",
                ip_address=ip_address,
                user_agent=user_agent,
                outcome="failure",
                detail=f"Unknown email: {email}",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials.",
            )

        # Check account lockout
        if user.is_locked:
            self._audit.log(
                "LOGIN_FAILED",
                actor_id=user.id,
                actor_uuid=str(user.uuid),
                ip_address=ip_address,
                user_agent=user_agent,
                outcome="failure",
                detail="Account locked",
            )
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked. Please try again later.",
            )

        if not verify_password(password, user.password_hash):
            self._user_repo.increment_failed_login(user)
            if user.failed_login_count >= self._cfg.MAX_LOGIN_ATTEMPTS:
                lock_until = datetime.now(timezone.utc) + timedelta(
                    minutes=self._cfg.ACCOUNT_LOCKOUT_MINUTES
                )
                self._user_repo.lock_account(user, lock_until)
                self._audit.log(
                    "ACCOUNT_LOCKED",
                    actor_id=user.id,
                    actor_uuid=str(user.uuid),
                    ip_address=ip_address,
                    user_agent=user_agent,
                    outcome="warning",
                    detail=f"Locked until {lock_until.isoformat()}",
                )
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail="Too many failed attempts. Account locked.",
                )
            self._audit.log(
                "LOGIN_FAILED",
                actor_id=user.id,
                actor_uuid=str(user.uuid),
                ip_address=ip_address,
                user_agent=user_agent,
                outcome="failure",
                detail=f"Attempt {user.failed_login_count}/{self._cfg.MAX_LOGIN_ATTEMPTS}",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials.",
            )

        # Reset failed count on success
        self._user_repo.reset_failed_login(user)

        return self._issue_tokens(user, ip_address=ip_address, user_agent=user_agent)

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------
    def logout(self, jti: str) -> None:
        session = self._session_repo.get_by_jti(jti)
        if session:
            self._rt_repo.revoke_all_for_session(session.id)
            self._session_repo.revoke(session)
            self._audit.log(
                "LOGOUT",
                actor_id=session.user_id,
                detail="User logged out",
            )

    # ------------------------------------------------------------------
    # Token refresh
    # ------------------------------------------------------------------
    def refresh(self, raw_refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(raw_refresh_token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token.",
            )

        if not payload.refresh:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not a refresh token.",
            )

        token_hash = _hash_token(raw_refresh_token)
        rt = self._rt_repo.get_by_hash(token_hash)
        if not rt or not rt.is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked or expired.",
            )

        # Revoke old token (rotation)
        self._rt_repo.revoke(rt)

        user = self._user_repo.get_by_id(rt.session.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive.",
            )

        # Issue new pair in the SAME session
        return self._issue_tokens(
            user,
            existing_session=rt.session,
        )

    # ------------------------------------------------------------------
    # Current user retrieval (used by GET /auth/me)
    # ------------------------------------------------------------------
    def get_current_user(self, user_id: int) -> User:
        user = self._user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive.",
            )
        return user

    # ------------------------------------------------------------------
    # Password reset flow
    # ------------------------------------------------------------------
    def initiate_password_reset(self, email: str) -> Optional[str]:
        """
        Generate a secure reset token for the user.
        Returns the token (for emailing). Returns None if user not found
        (silent failure to prevent email enumeration).
        """
        user = self._user_repo.get_by_email(email)
        if not user or not user.is_active:
            return None

        token = secrets.token_urlsafe(48)
        user.password_reset_token = token
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        self._user_repo.save(user)

        self._audit.log(
            "PASSWORD_RESET_REQUESTED",
            actor_id=user.id,
            actor_uuid=str(user.uuid),
            resource_type="user",
            resource_id=str(user.uuid),
        )
        return token

    def complete_password_reset(self, token: str, new_password: str) -> None:
        user = self._user_repo.get_by_reset_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset token.",
            )
        # Delegate to UserService to enforce policy and history
        from app.services.user import UserService
        UserService(self._db).set_password_after_reset(user, new_password)

        self._audit.log(
            "PASSWORD_RESET",
            actor_id=user.id,
            actor_uuid=str(user.uuid),
            resource_type="user",
            resource_id=str(user.uuid),
        )
        # Revoke all sessions after password reset for security
        self._session_repo.revoke_all_for_user(user.id)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _issue_tokens(
        self,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        existing_session: Optional[UserSession] = None,
    ) -> TokenResponse:
        permission_codes = user.permission_codes if not user.is_superuser else ["*"]
        primary_role = user.roles[0].slug if user.roles else "none"

        access_token = create_access_token(
            subject=str(user.uuid),
            role=primary_role,
            permissions=permission_codes,
        )
        raw_refresh = create_refresh_token(subject=str(user.uuid))

        access_payload = decode_token(access_token)
        refresh_payload = decode_token(raw_refresh)

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=self._cfg.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expires_at = now + timedelta(days=self._cfg.REFRESH_TOKEN_EXPIRE_DAYS)

        if existing_session is None:
            session = UserSession(
                user_id=user.id,
                jti=access_payload.jti,
                ip_address=ip_address,
                user_agent=user_agent,
                device_type=self._detect_device(user_agent),
                browser=self._detect_browser(user_agent),
                login_at=now,
                expires_at=expires_at,
            )
            self._session_repo.create(session)
        else:
            session = existing_session
            session.jti = access_payload.jti
            session.expires_at = expires_at
            self._session_repo.save(session)

        rt = RefreshToken(
            session_id=session.id,
            token_hash=_hash_token(raw_refresh),
            jti=refresh_payload.jti,
            expires_at=refresh_expires_at,
        )
        self._rt_repo.create(rt)

        self._audit.log(
            "LOGIN",
            actor_id=user.id,
            actor_uuid=str(user.uuid),
            ip_address=ip_address,
            user_agent=user_agent,
            detail="Login successful",
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
            token_type="bearer",
            expires_in=self._cfg.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    @staticmethod
    def _detect_device(user_agent: Optional[str]) -> str:
        if not user_agent:
            return "unknown"
        ua = user_agent.lower()
        if any(x in ua for x in ("mobile", "android", "iphone")):
            return "mobile"
        if "tablet" in ua or "ipad" in ua:
            return "tablet"
        return "desktop"

    @staticmethod
    def _detect_browser(user_agent: Optional[str]) -> Optional[str]:
        if not user_agent:
            return None
        ua = user_agent.lower()
        for browser in ("chrome", "firefox", "safari", "edge", "opera"):
            if browser in ua:
                return browser.title()
        return "Other"
