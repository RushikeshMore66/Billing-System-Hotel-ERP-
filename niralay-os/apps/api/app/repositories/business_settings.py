"""
Business settings repository for NiralayOS.

Singleton pattern — one row in business_settings table.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.settings import BusinessSettings
from app.repositories.base import BaseRepository


class BusinessSettingsRepository(BaseRepository[BusinessSettings]):
    def __init__(self, db: Session) -> None:
        super().__init__(BusinessSettings, db)

    def get_singleton(self) -> Optional[BusinessSettings]:
        """Return the single business settings row, or None."""
        return self.db.query(BusinessSettings).filter(
            BusinessSettings.is_active.is_(True)
        ).first()

    def get_or_create_singleton(self) -> BusinessSettings:
        """Return existing settings or create defaults."""
        settings = self.get_singleton()
        if settings is None:
            settings = BusinessSettings()
            self.db.add(settings)
            self.db.flush()
            self.db.refresh(settings)
        return settings
