"""
AuditLog model for NiralayOS.

Append-only immutable record of every security-relevant event.
Never update or delete rows — only insert.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class AuditLog(Base):
    """
    Immutable security event log.

    One row per event. No updates. No deletes.

    Event codes (from constants.AuditEvent):
        LOGIN, LOGOUT, LOGIN_FAILED, ACCOUNT_LOCKED,
        PASSWORD_CHANGED, PASSWORD_RESET_REQUESTED, PASSWORD_RESET,
        USER_CREATED, USER_UPDATED, USER_DEACTIVATED,
        ROLE_ASSIGNED, ROLE_REVOKED,
        PERMISSION_ASSIGNED, PERMISSION_REVOKED,
        SESSION_EXPIRED, TOKEN_REFRESHED
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    actor_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who performed the action; NULL = system",
    )
    actor_uuid: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
        index=True,
        comment="Denormalized UUID snapshot for forensics after user deletion",
    )

    event: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Audit event code, e.g. LOGIN, PASSWORD_CHANGED",
    )
    resource_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="e.g. user, role, permission",
    )
    resource_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="ID or UUID of the affected resource",
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    outcome: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="success",
        server_default="success",
        comment="success | failure | warning",
    )
    detail: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Human-readable description of what happened",
    )
    metadata_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="JSON blob for structured additional context",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    # Relationships
    actor: Mapped[Optional[User]] = relationship(
        "User",
        back_populates="audit_logs",
        foreign_keys=[actor_id],
        lazy="selectin",
    )
