"""
Reservation models for NiralayOS.
"""

from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from sqlalchemy import ForeignKey, String, Integer, Numeric, Text, DateTime, Date, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base
from app.core.constants import ReservationStatus, ReservationSource


class Reservation(AuditMixin, Base):
    """
    Core reservation booking.
    """
    __tablename__ = "reservations"

    reservation_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    guest_id: Mapped[int] = mapped_column(ForeignKey("guests.id", ondelete="RESTRICT"), nullable=False, index=True)
    room_id: Mapped[Optional[int]] = mapped_column(ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True, index=True)
    room_type_id: Mapped[int] = mapped_column(ForeignKey("room_types.id", ondelete="RESTRICT"), nullable=False)
    
    check_in_date: Mapped[date] = mapped_column(Date, nullable=False)
    check_out_date: Mapped[date] = mapped_column(Date, nullable=False)
    nights: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    adults: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    children: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    status: Mapped[ReservationStatus] = mapped_column(SQLEnum(ReservationStatus), nullable=False, default=ReservationStatus.PENDING, index=True)
    source: Mapped[ReservationSource] = mapped_column(SQLEnum(ReservationSource), nullable=False, default=ReservationSource.DIRECT)
    
    rate_plan_id: Mapped[Optional[int]] = mapped_column(ForeignKey("rate_plans.id", ondelete="SET NULL"), nullable=True)
    
    base_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    advance_paid: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    
    special_requests: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    guest: Mapped["Guest"] = relationship("Guest", back_populates="reservations", lazy="joined")
    room: Mapped[Optional["Room"]] = relationship("Room", lazy="joined")
    room_type: Mapped["RoomType"] = relationship("RoomType", lazy="joined")
    status_history: Mapped[list["ReservationStatusHistory"]] = relationship("ReservationStatusHistory", back_populates="reservation")


class ReservationStatusHistory(Base):
    """
    Log of status transitions for a reservation.
    """
    __tablename__ = "reservation_status_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reservation_id: Mapped[int] = mapped_column(ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False, index=True)
    from_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    reservation: Mapped["Reservation"] = relationship("Reservation", back_populates="status_history")
