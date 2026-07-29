"""
Guest models for NiralayOS.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import ForeignKey, String, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base


class Guest(AuditMixin, Base):
    """
    Guest profile holding personal and contact details.
    """
    __tablename__ = "guests"

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    
    id_type_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("guest_id_types.id", ondelete="SET NULL"),
        nullable=True,
    )
    id_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    nationality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default="Indian")
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    id_type: Mapped[Optional["GuestIDType"]] = relationship("GuestIDType")
    reservations: Mapped[list["Reservation"]] = relationship("Reservation", back_populates="guest")
