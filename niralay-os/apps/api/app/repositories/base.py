"""
Base repository providing generic CRUD for NiralayOS.

All Sprint 2 repositories inherit from BaseRepository[ModelT].
Repositories contain ONLY database I/O — no business logic.
"""

from __future__ import annotations

from typing import Generic, Optional, Type, TypeVar

from sqlalchemy.orm import Session

from app.database.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic CRUD repository."""

    def __init__(self, model: Type[ModelT], db: Session) -> None:
        self.model = model
        self.db = db

    def get_by_id(self, record_id: int) -> Optional[ModelT]:
        return self.db.get(self.model, record_id)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelT]:
        return (
            self.db.query(self.model)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count(self) -> int:
        return self.db.query(self.model).count()

    def create(self, instance: ModelT) -> ModelT:
        self.db.add(instance)
        self.db.flush()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: ModelT) -> None:
        self.db.delete(instance)
        self.db.flush()

    def save(self, instance: ModelT) -> ModelT:
        self.db.add(instance)
        self.db.flush()
        self.db.refresh(instance)
        return instance
