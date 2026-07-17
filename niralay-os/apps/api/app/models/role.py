"""
Role and Permission models for NiralayOS.

Roles are configurable containers of permissions.
Permissions are atomic module:action pairs (e.g. "reservation:approve").

Relationships:
    Role  ←→  Permission   (many-to-many via role_permissions)
    Role  ←→  User         (many-to-many via user_roles in user.py)
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base

if TYPE_CHECKING:
    from app.models.user import User


# ---------------------------------------------------------------------------
# Association table: roles ↔ permissions  (many-to-many)
# ---------------------------------------------------------------------------
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        Integer,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "granted_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Column("granted_by", String(255), nullable=True),
)


# ---------------------------------------------------------------------------
# Permission model
# ---------------------------------------------------------------------------
class Permission(AuditMixin, Base):
    """
    Atomic capability unit.

    Code format: ``module:action``  (e.g. ``reservation:approve``)
    Codes are immutable identifiers referenced in JWT payloads and
    in-code ``require_permission()`` calls.
    """

    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
        comment="module:action identifier, e.g. reservation:approve",
    )
    module: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        index=True,
        comment="Logical grouping (reservation, billing, kitchen, …)",
    )
    action: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        comment="Verb: view, create, edit, delete, approve, …",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
        lazy="selectin",
    )


# ---------------------------------------------------------------------------
# Role model
# ---------------------------------------------------------------------------
class Role(AuditMixin, Base):
    """
    Named collection of permissions.

    13 default hotel roles are seeded at startup.
    Additional roles can be created via the API.
    """

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
        comment="Human-readable role label, e.g. 'Receptionist'",
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
        comment="Machine-safe identifier, e.g. 'receptionist'",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="True = seeded role; cannot be deleted via API",
    )

    # Relationships
    permissions: Mapped[list[Permission]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin",
    )
    users: Mapped[list[User]] = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
        lazy="dynamic",
    )

    @property
    def permission_codes(self) -> list[str]:
        """Return all permission codes on this role."""
        return [p.code for p in self.permissions]
