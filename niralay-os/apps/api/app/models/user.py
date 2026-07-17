"""
User model for NiralayOS.

Stores core identity, authentication state, and account lockout fields.
M2M relationship to Role via the user_roles association table.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    Table,
    Column,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.session import Session as UserSession
    from app.models.audit_log import AuditLog
    from app.models.user import PasswordHistory, UserPreference


# ---------------------------------------------------------------------------
# Association table: users ↔ roles  (many-to-many)
# ---------------------------------------------------------------------------
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "assigned_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Column("assigned_by", String(255), nullable=True),
)


# ---------------------------------------------------------------------------
# User model
# ---------------------------------------------------------------------------
class User(AuditMixin, Base):
    """
    Core user identity record.

    One user can hold multiple roles (many-to-many).
    Password hashing is done in the service layer — never stored in plain text.
    """

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
        nullable=False,
        comment="Unique login handle",
    )
    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=False,
        comment="RFC 5321 email address",
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="bcrypt hash — NEVER expose",
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    avatar: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="URL or relative path to avatar image",
    )
    department: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
    )
    designation: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="active",
        server_default="active",
        comment="active | inactive | suspended",
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="Bypasses all permission checks",
    )

    # ------------------------------------------------------------------
    # Account lockout
    # ------------------------------------------------------------------
    failed_login_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Account is locked until this UTC timestamp",
    )

    # ------------------------------------------------------------------
    # Password reset
    # ------------------------------------------------------------------
    password_reset_token: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
    )
    password_reset_expires: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        lazy="selectin",
    )
    sessions: Mapped[list[UserSession]] = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    audit_logs: Mapped[list[AuditLog]] = relationship(
        "AuditLog",
        back_populates="actor",
        foreign_keys="AuditLog.actor_id",
        lazy="dynamic",
    )
    password_history: Mapped[list[PasswordHistory]] = relationship(
        "PasswordHistory",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="PasswordHistory.created_at.desc()",
        lazy="selectin",
    )
    preferences: Mapped[Optional[UserPreference]] = relationship(
        "UserPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def is_locked(self) -> bool:
        """True when the account is temporarily locked due to failed logins."""
        if self.locked_until is None:
            return False
        from datetime import timezone
        from datetime import datetime as _dt
        return _dt.now(timezone.utc) < self.locked_until

    @property
    def permission_codes(self) -> list[str]:
        """Flat list of all permission codes granted via this user's roles."""
        codes: set[str] = set()
        for role in self.roles:
            for perm in role.permissions:
                codes.add(perm.code)
        return list(codes)

    @property
    def role_names(self) -> list[str]:
        """Flat list of role names assigned to this user."""
        return [r.name for r in self.roles]


# ---------------------------------------------------------------------------
# Password history  (prevents reuse of last N passwords)
# ---------------------------------------------------------------------------
class PasswordHistory(Base):
    """Stores historical bcrypt hashes to prevent password reuse."""

    __tablename__ = "password_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="bcrypt hash of a previously used password",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped[User] = relationship("User", back_populates="password_history")

    __table_args__ = (
        UniqueConstraint("user_id", "password_hash", name="uq_user_password_hash"),
    )


# ---------------------------------------------------------------------------
# User preferences
# ---------------------------------------------------------------------------
class UserPreference(Base):
    """Per-user UI and notification preferences."""

    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="en",
        server_default="en",
    )
    timezone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Asia/Kolkata",
        server_default="Asia/Kolkata",
    )
    theme: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="system",
        server_default="system",
        comment="light | dark | system",
    )
    email_notifications: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped[User] = relationship("User", back_populates="preferences")
