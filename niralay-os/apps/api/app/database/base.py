"""
SQLAlchemy declarative base and shared column helpers.

All ORM models inherit from ``Base``.
The ``AuditMixin`` injects the mandatory audit columns required
by every table in NiralayOS:

    id, uuid, created_at, updated_at, created_by, updated_by,
    deleted_at, is_active

Usage:
    from app.database.base import Base, AuditMixin

    class Room(AuditMixin, Base):
        __tablename__ = "rooms"
        name: Mapped[str] = mapped_column(String(100))
"""

from __future__ import annotations

import uuid as _uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base.

    All models inherit from this class.
    Provides a default ``__repr__`` for debugging.
    """

    def __repr__(self) -> str:  # pragma: no cover
        cols = ", ".join(
            f"{c.key}={getattr(self, c.key)!r}"
            for c in self.__table__.columns
            if c.key in ("id", "uuid")
        )
        return f"<{self.__class__.__name__}({cols})>"

    def to_dict(self) -> dict[str, Any]:
        """Serialize model to a plain dict (excludes relationships)."""
        return {
            col.name: getattr(self, col.name)
            for col in self.__table__.columns
        }


class AuditMixin:
    """
    Mixin that adds standard audit columns to every table.

    Column order matches the specification:
        id, uuid, created_at, updated_at,
        created_by, updated_by, deleted_at, is_active
    """

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    uuid: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=_uuid.uuid4,
        unique=True,
        index=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        onupdate=_utc_now,
        server_default=func.now(),
        nullable=False,
    )

    created_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="UUID of the user who created this record",
    )

    updated_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="UUID of the user who last updated this record",
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Set when the record is soft-deleted; NULL = active",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="False = soft-deleted",
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self, deleted_by: str | None = None) -> None:
        """Mark this record as deleted without removing it from the DB."""
        self.deleted_at = _utc_now()
        self.is_active = False
        if deleted_by:
            self.updated_by = deleted_by

    def restore(self, restored_by: str | None = None) -> None:
        """Undo a soft-delete."""
        self.deleted_at = None
        self.is_active = True
        if restored_by:
            self.updated_by = restored_by
