"""
Business settings model for NiralayOS.

BusinessSettings is a singleton table — exactly one row exists.
Use BusinessSettingsRepository.get_or_create_singleton() to access it.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import AuditMixin, Base


class BusinessSettings(AuditMixin, Base):
    """
    Property-wide operational settings.

    Affects invoice numbering, date/currency formatting,
    and system-level backup preferences.
    """

    __tablename__ = "business_settings"

    # ── Numbering formats ──────────────────────────────────────────────────
    invoice_number_format: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="INV-{YYYY}-{MM}-{SEQ}",
        comment="Format tokens: {YYYY} {MM} {DD} {SEQ} {PREFIX}",
    )
    reservation_number_format: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="RES-{YYYY}-{SEQ}",
    )
    invoice_sequence_start: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    reservation_sequence_start: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    # ── Localisation ───────────────────────────────────────────────────────
    timezone: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
        default="Asia/Kolkata",
    )
    date_format: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="DD/MM/YYYY",
        comment="e.g. DD/MM/YYYY | MM-DD-YYYY | YYYY-MM-DD",
    )
    time_format: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="12h",
        comment="12h | 24h",
    )
    currency_format: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="symbol_before",
        comment="symbol_before | symbol_after | code_before",
    )
    decimal_precision: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=2,
        comment="Number of decimal places for monetary amounts",
    )
    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="en",
    )

    # ── Backup settings ─────────────────────────────────────────────────────
    auto_backup_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    auto_backup_frequency: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="daily",
        comment="daily | weekly | monthly",
    )
    backup_retention_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30,
    )
    backup_storage_path: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )

    # ── Operational defaults ─────────────────────────────────────────────
    tax_inclusive_by_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    allow_partial_payment: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    minimum_advance_payment_pct: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Minimum advance payment as % of total (0 = none required)",
    )
    additional_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
