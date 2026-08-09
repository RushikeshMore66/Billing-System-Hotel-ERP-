"""
Expense models for NiralayOS.

Covers expense management:
    ExpenseCategory, Expense

Every expense is categorised, dated, and optionally linked to
an uploaded receipt document.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base


# ---------------------------------------------------------------------------
# ExpenseCategory
# ---------------------------------------------------------------------------
class ExpenseCategory(AuditMixin, Base):
    """
    Configurable expense classification.

    Examples: Staff Salaries, Utilities, Maintenance, Food & Beverage Purchases,
              Marketing, Insurance, Housekeeping Supplies, Laundry.
    """

    __tablename__ = "expense_categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_system: Mapped[bool] = mapped_column(
        Integer,  # Using Integer as boolean for SQLite compatibility
        nullable=False,
        default=False,
        comment="System categories cannot be deleted",
    )

    # Relationships
    expenses: Mapped[list["Expense"]] = relationship(
        "Expense",
        back_populates="category",
        lazy="dynamic",
    )

    __table_args__ = (
        UniqueConstraint("name", name="uq_expense_categories_name"),
        Index("ix_expense_categories_display_order", "display_order"),
    )


# ---------------------------------------------------------------------------
# Expense
# ---------------------------------------------------------------------------
class Expense(AuditMixin, Base):
    """
    A single expense record.

    Expenses feed into the financial reporting system.
    Receipt documents are linked via the file_upload entity system.
    """

    __tablename__ = "expenses"

    category_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("expense_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Expense amount in default currency",
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0"),
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="amount + tax_amount",
    )
    expense_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Date the expense was incurred",
    )
    payment_method: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
        comment="cash | upi | credit_card | debit_card | bank_transfer | other",
    )
    vendor_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    vendor_contact: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reference_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Invoice or receipt reference number",
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Receipt document (links to UploadedFile)
    receipt_file_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("uploaded_files.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    category: Mapped[Optional["ExpenseCategory"]] = relationship(
        "ExpenseCategory",
        back_populates="expenses",
        lazy="joined",
    )

    __table_args__ = (
        Index("ix_expenses_expense_date", "expense_date"),
        Index("ix_expenses_category_id", "category_id"),
        Index("ix_expenses_payment_method", "payment_method"),
    )
