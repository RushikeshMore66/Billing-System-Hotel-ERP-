"""
Business settings service for NiralayOS.

Singleton upsert logic — always exactly one settings row.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.settings import BusinessSettings
from app.repositories.business_settings import BusinessSettingsRepository
from app.schemas.business_settings import BusinessSettingsUpdate


class BusinessSettingsService:
    def __init__(self, db: Session) -> None:
        self._repo = BusinessSettingsRepository(db)

    def get(self) -> BusinessSettings:
        """Return (or create default) business settings."""
        return self._repo.get_or_create_singleton()

    def update(
        self,
        data: BusinessSettingsUpdate,
        updated_by: Optional[str] = None,
    ) -> BusinessSettings:
        settings = self._repo.get_or_create_singleton()
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(settings, field, value)
        settings.updated_by = updated_by
        return self._repo.save(settings)
