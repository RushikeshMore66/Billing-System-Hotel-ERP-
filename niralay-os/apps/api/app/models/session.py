"""
Session and RefreshToken models for NiralayOS.

Sessions track one login per device/browser.
RefreshTokens are rotating single-use tokens stored as hashed values.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base

if TYPE_CHECKING:
    from app.models.user import User


# ---------------------------------------------------------------------------
# Session model
# ---------------------------------------------------------------------------
class Session(AuditMixin, Base):
    """
    Login session record.

    One session per device login.  Multiple sessions allowed per user.
    Invalidated on logout or on token expiry.
    """

    __tablename__ = "sessions"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    jti: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="JWT ID of the access token that created this session",
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="IPv4 or IPv6 client address",
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Full User-Agent string from the login request",
    )
    device_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="desktop | mobile | tablet | bot | unknown",
    )
    browser: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    os: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    login_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    logout_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="When the access token expires",
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="sessions")
    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        "RefreshToken",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    @property
    def is_active(self) -> bool:  # type: ignore[override]
        """Session is active when not revoked and not logged out."""
        from datetime import timezone
        from datetime import datetime as _dt
        now = _dt.now(timezone.utc)
        return (
            not self.is_revoked
            and self.logout_at is None
            and self.expires_at > now
        )


# ---------------------------------------------------------------------------
# Refresh token model
# ---------------------------------------------------------------------------
class RefreshToken(Base):
    """
    Rotating refresh token.

    Stored as a bcrypt-hashed value.
    On each /auth/refresh call the old token is revoked and a new one issued.
    """

    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="SHA-256 hash of the raw refresh token string",
    )
    jti: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="JWT ID embedded in the token payload",
    )
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # Relationships
    session: Mapped[Session] = relationship("Session", back_populates="refresh_tokens")

    @property
    def is_valid(self) -> bool:
        """Token is valid when not revoked and not expired."""
        from datetime import timezone
        from datetime import datetime as _dt
        return not self.is_revoked and self.expires_at > _dt.now(timezone.utc)
