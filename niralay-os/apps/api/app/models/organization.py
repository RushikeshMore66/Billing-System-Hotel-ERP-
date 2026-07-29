"""
Organisation structure models for NiralayOS.

Covers:
    Department   — functional groups (Reception, Kitchen, Housekeeping …)
    Designation  — job roles within departments (Manager, Chef, Waiter …)
    GuestIDType  — accepted identity documents (Aadhaar, Passport, PAN …)
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base


class Department(AuditMixin, Base):
    """
    Functional department within the hotel.

    System departments (Reception, Restaurant, Kitchen, Housekeeping,
    Maintenance, Accounts) are seeded at startup and cannot be deleted.
    """

    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Machine-safe code, e.g. RECEPTION",
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="System departments cannot be deleted",
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    designations: Mapped[list["Designation"]] = relationship(
        "Designation",
        back_populates="department",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("code", name="uq_departments_code"),
        UniqueConstraint("name", name="uq_departments_name"),
    )


class Designation(AuditMixin, Base):
    """
    Job role / position within the hotel.

    Linked to a department; one designation belongs to one department.
    """

    __tablename__ = "designations"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Machine-safe code, e.g. HEAD_CHEF",
    )
    department_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    department: Mapped[Optional["Department"]] = relationship(
        "Department",
        back_populates="designations",
    )

    __table_args__ = (
        UniqueConstraint("code", name="uq_designations_code"),
    )


class GuestIDType(AuditMixin, Base):
    """
    Identity document types accepted during guest check-in.

    System types (Aadhaar, Passport, Driving License, PAN, Voter ID)
    are seeded at startup.
    """

    __tablename__ = "guest_id_types"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Machine-safe code, e.g. AADHAAR",
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    requires_expiry: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="True for documents with expiry dates (Passport, DL)",
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("code", name="uq_guest_id_types_code"),
        UniqueConstraint("name", name="uq_guest_id_types_name"),
    )
