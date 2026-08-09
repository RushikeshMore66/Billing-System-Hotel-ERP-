"""
Billing models for NiralayOS.

Covers the minimum viable billing system:
    Bill, BillItem, Payment

A Bill can be:
  - Reservation bill: linked to a reservation (room + services)
  - Restaurant bill: standalone table order
  - Mixed: both reservation and table

A Bill goes through: DRAFT → ISSUED → PAID / PARTIALLY_PAID
It can also be VOID or REFUNDED.

Payments reference a Bill and a PaymentMethod.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base


# ---------------------------------------------------------------------------
# Bill
# ---------------------------------------------------------------------------
class Bill(AuditMixin, Base):
    """
    A billing document covering charges for a guest stay and/or restaurant order.

    bill_number is generated from BusinessSettings.invoice_number_format.
    """

    __tablename__ = "bills"

    bill_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )
    bill_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
    )

    # Optional links
    reservation_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("reservations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    guest_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("guests.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    table_number: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Restaurant table number if this is a table bill",
    )

    # Bill type
    bill_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="room",
        comment="room | restaurant | mixed | other",
    )

    # Financial totals
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0"),
        comment="Sum of all item amounts before tax and discount",
    )
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0"),
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0"),
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0"),
        comment="subtotal - discount_amount + tax_amount",
    )
    amount_paid: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0"),
        comment="Sum of all successful payments",
    )
    amount_due: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0"),
        comment="total_amount - amount_paid",
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="draft",
        comment="draft | issued | paid | partially_paid | void | refunded",
        index=True,
    )

    # Billing details
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # GST / tax details for invoice
    gst_number: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    hsn_sac_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Void info
    void_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    voided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    voided_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    items: Mapped[list["BillItem"]] = relationship(
        "BillItem",
        back_populates="bill",
        cascade="all, delete-orphan",
        order_by="BillItem.display_order",
        lazy="selectin",
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="bill",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_bills_bill_date", "bill_date"),
        Index("ix_bills_status", "status"),
        Index("ix_bills_reservation_id", "reservation_id"),
        Index("ix_bills_guest_id", "guest_id"),
    )


# ---------------------------------------------------------------------------
# BillItem
# ---------------------------------------------------------------------------
class BillItem(Base):
    """
    A single line item on a bill.

    Can represent:
      - Room charge (nightly rate × nights)
      - Restaurant menu item
      - Service charge (laundry, minibar, etc.)
      - Tax line (if itemised)
      - Discount line (negative amount)
    """

    __tablename__ = "bill_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    bill_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # What this line represents
    item_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="service",
        comment="room | menu_item | service | tax | discount | other",
    )
    description: Mapped[str] = mapped_column(String(500), nullable=False)

    # Optional links to source entities
    menu_item_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("menu_items.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Quantities and pricing
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),
        nullable=False,
        default=Decimal("1"),
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    discount_pct: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0"),
    )
    tax_rate: Mapped[Decimal] = mapped_column(
        Numeric(6, 2),
        nullable=False,
        default=Decimal("0"),
        comment="GST percentage applicable to this line",
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="quantity × unit_price × (1 - discount_pct/100)",
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0"),
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="amount + tax_amount",
    )

    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    bill: Mapped["Bill"] = relationship("Bill", back_populates="items")

    __table_args__ = (
        Index("ix_bill_items_bill_id", "bill_id"),
        Index("ix_bill_items_item_type", "item_type"),
    )


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------
class Payment(AuditMixin, Base):
    """
    A payment transaction against a bill.

    Multiple payments can be applied to one bill (partial payments).
    The bill's amount_paid is the sum of all successful payments.
    """

    __tablename__ = "payments"

    bill_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bills.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    payment_method_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("payment_methods.id", ondelete="SET NULL"),
        nullable=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    payment_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="success",
        comment="pending | success | failed | refunded",
        index=True,
    )

    # Reference / transaction ID (for UPI, card, bank transfer)
    reference_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Payment type shorthand (denormalised for reporting)
    payment_type: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
        comment="cash | upi | credit_card | debit_card | net_banking | wallet | bank_transfer",
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # For refunds
    is_refund: Mapped[bool] = mapped_column(
        Integer,
        nullable=False,
        default=False,
    )
    original_payment_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("payments.id", ondelete="SET NULL"),
        nullable=True,
    )

    received_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    bill: Mapped["Bill"] = relationship("Bill", back_populates="payments")

    __table_args__ = (
        Index("ix_payments_bill_id", "bill_id"),
        Index("ix_payments_payment_date", "payment_date"),
        Index("ix_payments_status", "status"),
        Index("ix_payments_payment_type", "payment_type"),
    )
