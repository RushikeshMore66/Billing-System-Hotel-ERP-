"""
Inventory service for NiralayOS.

Business logic for inventory management.
All stock changes MUST go through record_movement() — never update
current_stock directly on the item.
"""

from __future__ import annotations

from datetime import date, timezone, datetime
from decimal import Decimal
from typing import Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.inventory import InventoryCategory, InventoryItem, StockMovement, StoreLocation
from app.repositories.inventory import (
    InventoryCategoryRepository,
    InventoryItemRepository,
    StockMovementRepository,
    StoreLocationRepository,
)
from app.schemas.inventory import (
    InventoryCategoryCreate,
    InventoryCategoryUpdate,
    InventoryItemCreate,
    InventoryItemUpdate,
    StockMovementCreate,
    StoreLocationCreate,
    StoreLocationUpdate,
)

# Movement types that increase stock (positive direction)
_ADDITIVE_TYPES = {"opening", "purchase", "return_in", "transfer_in"}
# Movement types that decrease stock (negative direction)
_SUBTRACTIVE_TYPES = {"consumption", "damage", "loss", "transfer_out"}


class InventoryCategoryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = InventoryCategoryRepository(db)

    def list_all(self) -> Sequence[InventoryCategory]:
        return self.repo.list_all()

    def get(self, category_id: int) -> InventoryCategory:
        cat = self.repo.get_by_id(category_id)
        if not cat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return cat

    def create(self, data: InventoryCategoryCreate) -> InventoryCategory:
        if self.repo.name_exists(data.name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category '{data.name}' already exists",
            )
        cat = InventoryCategory(**data.model_dump())
        return self.repo.create(cat)

    def update(self, category_id: int, data: InventoryCategoryUpdate) -> InventoryCategory:
        cat = self.get(category_id)
        update_data = data.model_dump(exclude_unset=True)
        if "name" in update_data and self.repo.name_exists(update_data["name"], exclude_id=category_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category '{update_data['name']}' already exists",
            )
        for key, value in update_data.items():
            setattr(cat, key, value)
        return self.repo.save(cat)

    def delete(self, category_id: int) -> None:
        cat = self.get(category_id)
        cat.soft_delete()
        self.repo.save(cat)


class StoreLocationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = StoreLocationRepository(db)

    def list_all(self) -> Sequence[StoreLocation]:
        return self.repo.list_all()

    def get(self, location_id: int) -> StoreLocation:
        loc = self.repo.get_by_id(location_id)
        if not loc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
        return loc

    def create(self, data: StoreLocationCreate) -> StoreLocation:
        if self.repo.code_exists(data.code):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Location with code '{data.code}' already exists",
            )
        loc = StoreLocation(**data.model_dump())
        return self.repo.create(loc)

    def update(self, location_id: int, data: StoreLocationUpdate) -> StoreLocation:
        loc = self.get(location_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(loc, key, value)
        return self.repo.save(loc)

    def delete(self, location_id: int) -> None:
        loc = self.get(location_id)
        loc.soft_delete()
        self.repo.save(loc)


class InventoryItemService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = InventoryItemRepository(db)
        self.movement_repo = StockMovementRepository(db)

    def get(self, item_id: int) -> InventoryItem:
        item = self.repo.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
        return item

    def search(
        self,
        query: Optional[str] = None,
        category_id: Optional[int] = None,
        location_id: Optional[int] = None,
        item_type: Optional[str] = None,
        stock_level: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[InventoryItem], int]:
        return self.repo.search(
            query=query,
            category_id=category_id,
            location_id=location_id,
            item_type=item_type,
            stock_level=stock_level,
            skip=skip,
            limit=limit,
        )

    def create(self, data: InventoryItemCreate, recorded_by: Optional[str] = None) -> InventoryItem:
        if self.repo.sku_exists(data.sku):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Item with SKU '{data.sku}' already exists",
            )

        opening_stock = data.current_stock
        item_data = data.model_dump()
        item_data["current_stock"] = Decimal("0")  # Start at 0, will add opening movement
        item = InventoryItem(**item_data)
        item = self.repo.create(item)

        # Record opening stock movement if non-zero
        if opening_stock > 0:
            self._create_movement(
                item=item,
                movement_type="opening",
                quantity=opening_stock,
                unit_cost=data.purchase_price,
                notes="Opening stock",
                recorded_by=recorded_by,
            )

        return item

    def update(self, item_id: int, data: InventoryItemUpdate) -> InventoryItem:
        item = self.get(item_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        return self.repo.save(item)

    def delete(self, item_id: int) -> None:
        item = self.get(item_id)
        item.soft_delete()
        self.repo.save(item)

    def record_movement(
        self,
        data: StockMovementCreate,
        recorded_by: Optional[str] = None,
    ) -> StockMovement:
        item = self.get(data.item_id)

        # Determine actual quantity change
        quantity = data.quantity
        if data.movement_type == "adjustment":
            # For adjustments, quantity can be signed (positive = increase, negative = decrease)
            # However the schema enforces gt=0, so we compute the absolute correction
            # The sign is carried in the movement_type context
            actual_change = quantity  # Positive adjustment adds stock
        elif data.movement_type in _ADDITIVE_TYPES:
            actual_change = quantity
        elif data.movement_type in _SUBTRACTIVE_TYPES:
            actual_change = -quantity
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown movement_type: {data.movement_type}",
            )

        new_stock = item.current_stock + actual_change
        if new_stock < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Insufficient stock. Current: {item.current_stock} {item.unit}, "
                    f"requested: {quantity} {item.unit}"
                ),
            )

        movement = self._create_movement(
            item=item,
            movement_type=data.movement_type,
            quantity=quantity,
            unit_cost=data.unit_cost,
            reference_type=data.reference_type,
            reference_id=data.reference_id,
            supplier_name=data.supplier_name,
            from_location_id=data.from_location_id,
            to_location_id=data.to_location_id,
            movement_date=data.movement_date,
            notes=data.notes,
            recorded_by=recorded_by,
        )
        return movement

    def get_movements(
        self,
        item_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[StockMovement], int]:
        self.get(item_id)  # Validate exists
        return self.movement_repo.list_for_item(item_id, skip=skip, limit=limit)

    def get_low_stock_items(self, limit: int = 20) -> Sequence[InventoryItem]:
        return self.repo.get_low_stock_items(limit=limit)

    def _create_movement(
        self,
        item: InventoryItem,
        movement_type: str,
        quantity: Decimal,
        unit_cost: Optional[Decimal] = None,
        reference_type: Optional[str] = None,
        reference_id: Optional[str] = None,
        supplier_name: Optional[str] = None,
        from_location_id: Optional[int] = None,
        to_location_id: Optional[int] = None,
        movement_date: Optional[date] = None,
        notes: Optional[str] = None,
        recorded_by: Optional[str] = None,
    ) -> StockMovement:
        """Core movement recorder — updates stock atomically."""
        if movement_type in _ADDITIVE_TYPES:
            actual_change = quantity
        elif movement_type in _SUBTRACTIVE_TYPES:
            actual_change = -quantity
        else:
            actual_change = quantity  # adjustment

        stock_before = item.current_stock
        stock_after = stock_before + actual_change

        total_cost = None
        if unit_cost is not None:
            total_cost = unit_cost * quantity

        movement = StockMovement(
            item_id=item.id,
            movement_type=movement_type,
            quantity=quantity,
            stock_before=stock_before,
            stock_after=stock_after,
            unit_cost=unit_cost,
            total_cost=total_cost,
            reference_type=reference_type,
            reference_id=reference_id,
            supplier_name=supplier_name,
            from_location_id=from_location_id,
            to_location_id=to_location_id,
            movement_date=movement_date or datetime.now(timezone.utc).date(),
            notes=notes,
            recorded_by=recorded_by,
        )
        self.movement_repo.create_movement(movement)

        # Update item's current stock
        item.current_stock = stock_after
        self.repo.save(item)

        # Also update last purchase price if this is a purchase
        if movement_type == "purchase" and unit_cost is not None:
            item.purchase_price = unit_cost
            self.repo.save(item)

        return movement
