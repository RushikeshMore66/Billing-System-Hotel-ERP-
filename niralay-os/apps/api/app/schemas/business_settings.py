"""
Business settings schemas for NiralayOS.

BusinessSettings is a singleton — no Create or Delete, only Get and Update.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class BusinessSettingsUpdate(BaseModel):
    """PATCH /settings/business — all fields optional."""

    invoice_number_format: Optional[str] = Field(None, max_length=100)
    reservation_number_format: Optional[str] = Field(None, max_length=100)
    invoice_sequence_start: Optional[int] = Field(None, ge=1)
    reservation_sequence_start: Optional[int] = Field(None, ge=1)
    timezone: Optional[str] = Field(None, max_length=60)
    date_format: Optional[str] = Field(
        None,
        pattern=r"^(DD/MM/YYYY|MM/DD/YYYY|YYYY-MM-DD|DD-MM-YYYY|MM-DD-YYYY)$",
    )
    time_format: Optional[str] = Field(None, pattern=r"^(12h|24h)$")
    currency_format: Optional[str] = Field(
        None,
        pattern=r"^(symbol_before|symbol_after|code_before)$",
    )
    decimal_precision: Optional[int] = Field(None, ge=0, le=4)
    language: Optional[str] = Field(None, max_length=10)
    auto_backup_enabled: Optional[bool] = None
    auto_backup_frequency: Optional[str] = Field(
        None,
        pattern=r"^(daily|weekly|monthly)$",
    )
    backup_retention_days: Optional[int] = Field(None, ge=1, le=365)
    backup_storage_path: Optional[str] = Field(None, max_length=512)
    tax_inclusive_by_default: Optional[bool] = None
    allow_partial_payment: Optional[bool] = None
    minimum_advance_payment_pct: Optional[int] = Field(None, ge=0, le=100)
    additional_notes: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "invoice_number_format": "INV-{YYYY}-{MM}-{SEQ}",
                "date_format": "DD/MM/YYYY",
                "time_format": "12h",
                "decimal_precision": 2,
                "auto_backup_enabled": True,
                "auto_backup_frequency": "daily",
            }]
        }
    }


class BusinessSettingsOut(BaseModel):
    id: int
    uuid: UUID
    invoice_number_format: str
    reservation_number_format: str
    invoice_sequence_start: int
    reservation_sequence_start: int
    timezone: str
    date_format: str
    time_format: str
    currency_format: str
    decimal_precision: int
    language: str
    auto_backup_enabled: bool
    auto_backup_frequency: str
    backup_retention_days: int
    backup_storage_path: Optional[str] = None
    tax_inclusive_by_default: bool
    allow_partial_payment: bool
    minimum_advance_payment_pct: int
    additional_notes: Optional[str] = None
    is_active: bool
    updated_at: datetime

    model_config = {"from_attributes": True}
