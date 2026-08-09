"""
Inventory repository for NiralayOS.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional, Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.inventory import InventoryCategory, InventoryItem, StockMovement, StoreLocation
from app.repositories.base import BaseRepository


class InventoryCategoryRepository(BaseRepository[InventoryCategory]):
    def __init__(self, db: Session) -> None:
        super().__init__(InventoryCategory, db)

    def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        stmt = select(self.model).where(
            func.lower(self.model.name) == name.lower(),
            self.model.is_active.is_(True),
        )
        if exclude_id:
            stmt = stmt.where(self.model.id != exclude_id)
        return self.db.scalars(stmt).first() is not None

    def list_all(self, active_only: bool = True) -> Sequence[InventoryCategory]:
        stmt = select(self.model).order_by(self.model.display_order, self.model.name)
        if active_only:
            stmt = stmt.where(self.model.is_active.is_(True))
        return self.db.scalars(stmt).all()


class StoreLocationRepository(BaseRepository[StoreLocation]):
    def __init__(self, db: Session) -> None:
        super().__init__(StoreLocation, db)

    def code_exists(self, code: str, exclude_id: Optional[int] = None) -> bool:
        stmt = select(self.model).where(
            func.lower(self.model.code) == code.lower(),
            self.model.is_active.is_(True),
        )
        if exclude_id:
            stmt = stmt.where(self.model.id != exclude_id)
        return self.db.scalars(stmt).first() is not None

    def list_all(self, active_only: bool = True) -> Sequence[StoreLocation]:
        stmt = select(self.model).order_by(self.model.display_order, self.model.name)
        if active_only:
            stmt = stmt.where(self.model.is_active.is_(True))
        return self.db.scalars(stmt).all()


class InventoryItemRepository(BaseRepository[InventoryItem]):
    def __init__(self, db: Session) -> None:
        super().__init__(InventoryItem, db)

    def sku_exists(self, sku: str, exclude_id: Optional[int] = None) -> bool:
        stmt = select(self.model).where(self.model.sku == sku)
        if exclude_id:
            stmt = stmt.where(self.model.id != exclude_id)
        return self.db.scalars(stmt).first() is not None

    def search(
        self,
        query: Optional[str] = None,
        category_id: Optional[int] = None,
        location_id: Optional[int] = None,
        item_type: Optional[str] = None,
        stock_level: Optional[str] = None,  # ok | low | critical
        active_only: bool = True,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[InventoryItem], int]:
        stmt = select(self.model)

        if active_only:
            stmt = stmt.where(self.model.is_active.is_(True))

        if query:
            stmt = stmt.where(
                or_(
                    self.model.name.ilike(f"%{query}%"),
                    self.model.sku.ilike(f"%{query}%"),
                    self.model.supplier_name.ilike(f"%{query}%"),
                )
            )

        if category_id is not None:
            stmt = stmt.where(self.model.category_id == category_id)

        if location_id is not None:
            stmt = stmt.where(self.model.location_id == location_id)

        if item_type:
            stmt = stmt.where(self.model.item_type == item_type)

        # Filter by stock level requires computed comparison
        if stock_level == "critical":
            stmt = stmt.where(
                self.model.minimum_stock > 0,
                self.model.current_stock <= self.model.minimum_stock * Decimal("0.4"),
            )
        elif stock_level == "low":
            stmt = stmt.where(
                self.model.minimum_stock > 0,
                self.model.current_stock > self.model.minimum_stock * Decimal("0.4"),
                self.model.current_stock <= self.model.minimum_stock * Decimal("0.8"),
            )
        elif stock_level == "ok":
            stmt = stmt.where(
                or_(
                    self.model.minimum_stock == 0,
                    self.model.current_stock > self.model.minimum_stock * Decimal("0.8"),
                )
            )

        stmt = stmt.order_by(self.model.name)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.scalar(count_stmt) or 0

        stmt = stmt.offset(skip).limit(limit)
        items = self.db.scalars(stmt).all()
        return items, total

    def get_low_stock_items(self, limit: int = 20) -> Sequence[InventoryItem]:
        """Return items at or below minimum stock threshold."""
        stmt = (
            select(self.model)
            .where(
                self.model.is_active.is_(True),
                self.model.minimum_stock > 0,
                self.model.current_stock <= self.model.minimum_stock,
            )
            .order_by(
                # critical first (stock/min ratio ascending)
                (self.model.current_stock / self.model.minimum_stock).asc()
            )
            .limit(limit)
        )
        return self.db.scalars(stmt).all()


class StockMovementRepository(BaseRepository[StockMovement]):
    def __init__(self, db: Session) -> None:
        super().__init__(StockMovement, db)

    def list_for_item(
        self,
        item_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[StockMovement], int]:
        stmt = (
            select(self.model)
            .where(self.model.item_id == item_id)
            .order_by(self.model.movement_date.desc(), self.model.id.desc())
        )
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        stmt = stmt.offset(skip).limit(limit)
        return self.db.scalars(stmt).all(), total

    def create_movement(self, movement: StockMovement) -> StockMovement:
        self.db.add(movement)
        self.db.flush()
        return movement
