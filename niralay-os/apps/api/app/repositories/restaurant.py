"""
Restaurant configuration repositories for NiralayOS.

Pure database I/O — no business logic.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.restaurant import (
    KitchenStation,
    MenuCategory,
    MenuItem,
    MenuModifier,
    MenuModifierOption,
    RestaurantCategory,
    RestaurantTable,
)
from app.repositories.base import BaseRepository


# ---------------------------------------------------------------------------
# RestaurantCategory
# ---------------------------------------------------------------------------
class RestaurantCategoryRepository(BaseRepository[RestaurantCategory]):
    def __init__(self, db: Session) -> None:
        super().__init__(RestaurantCategory, db)

    def list_active(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> tuple[list[RestaurantCategory], int]:
        q = self.db.query(RestaurantCategory).filter(RestaurantCategory.is_active.is_(True))
        if search:
            q = q.filter(RestaurantCategory.name.ilike(f"%{search}%"))
        total = q.count()
        items = q.order_by(RestaurantCategory.display_order, RestaurantCategory.name).offset(skip).limit(limit).all()
        return items, total

    def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(RestaurantCategory.id).filter(RestaurantCategory.name == name)
        if exclude_id:
            q = q.filter(RestaurantCategory.id != exclude_id)
        return q.first() is not None


# ---------------------------------------------------------------------------
# MenuCategory
# ---------------------------------------------------------------------------
class MenuCategoryRepository(BaseRepository[MenuCategory]):
    def __init__(self, db: Session) -> None:
        super().__init__(MenuCategory, db)

    def list_active(
        self,
        skip: int = 0,
        limit: int = 200,
        search: Optional[str] = None,
        restaurant_category_id: Optional[int] = None,
        parent_id: Optional[int] = None,
    ) -> tuple[list[MenuCategory], int]:
        q = self.db.query(MenuCategory).filter(MenuCategory.is_active.is_(True))
        if search:
            q = q.filter(MenuCategory.name.ilike(f"%{search}%"))
        if restaurant_category_id is not None:
            q = q.filter(MenuCategory.restaurant_category_id == restaurant_category_id)
        if parent_id is not None:
            q = q.filter(MenuCategory.parent_id == parent_id)
        total = q.count()
        items = q.order_by(MenuCategory.display_order, MenuCategory.name).offset(skip).limit(limit).all()
        return items, total


# ---------------------------------------------------------------------------
# KitchenStation
# ---------------------------------------------------------------------------
class KitchenStationRepository(BaseRepository[KitchenStation]):
    def __init__(self, db: Session) -> None:
        super().__init__(KitchenStation, db)

    def list_active(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> tuple[list[KitchenStation], int]:
        q = self.db.query(KitchenStation).filter(KitchenStation.is_active.is_(True))
        if search:
            q = q.filter(KitchenStation.name.ilike(f"%{search}%"))
        total = q.count()
        items = q.order_by(KitchenStation.display_order, KitchenStation.name).offset(skip).limit(limit).all()
        return items, total

    def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(KitchenStation.id).filter(KitchenStation.name == name)
        if exclude_id:
            q = q.filter(KitchenStation.id != exclude_id)
        return q.first() is not None


# ---------------------------------------------------------------------------
# MenuItem
# ---------------------------------------------------------------------------
class MenuItemRepository(BaseRepository[MenuItem]):
    def __init__(self, db: Session) -> None:
        super().__init__(MenuItem, db)

    def list_active(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        menu_category_id: Optional[int] = None,
        kitchen_station_id: Optional[int] = None,
        food_type: Optional[str] = None,
        is_available: Optional[bool] = None,
        sort_by: str = "name",
        sort_dir: str = "asc",
    ) -> tuple[list[MenuItem], int]:
        q = self.db.query(MenuItem).filter(MenuItem.is_active.is_(True))
        if search:
            term = f"%{search}%"
            q = q.filter(
                or_(
                    MenuItem.name.ilike(term),
                    MenuItem.item_code.ilike(term),
                )
            )
        if menu_category_id is not None:
            q = q.filter(MenuItem.menu_category_id == menu_category_id)
        if kitchen_station_id is not None:
            q = q.filter(MenuItem.kitchen_station_id == kitchen_station_id)
        if food_type:
            q = q.filter(MenuItem.food_type == food_type)
        if is_available is not None:
            q = q.filter(MenuItem.is_available.is_(is_available))
        total = q.count()
        sort_col = getattr(MenuItem, sort_by, MenuItem.name)
        if sort_dir == "desc":
            sort_col = sort_col.desc()
        items = q.order_by(sort_col).offset(skip).limit(limit).all()
        return items, total

    def item_code_exists(self, code: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(MenuItem.id).filter(MenuItem.item_code == code)
        if exclude_id:
            q = q.filter(MenuItem.id != exclude_id)
        return q.first() is not None

    def get_by_ids(self, ids: list[int]) -> list[MenuItem]:
        if not ids:
            return []
        return self.db.query(MenuItem).filter(MenuItem.id.in_(ids)).all()


# ---------------------------------------------------------------------------
# MenuModifier
# ---------------------------------------------------------------------------
class MenuModifierRepository(BaseRepository[MenuModifier]):
    def __init__(self, db: Session) -> None:
        super().__init__(MenuModifier, db)

    def list_active(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        modifier_type: Optional[str] = None,
    ) -> tuple[list[MenuModifier], int]:
        q = self.db.query(MenuModifier).filter(MenuModifier.is_active.is_(True))
        if search:
            q = q.filter(MenuModifier.name.ilike(f"%{search}%"))
        if modifier_type:
            q = q.filter(MenuModifier.modifier_type == modifier_type)
        total = q.count()
        items = q.order_by(MenuModifier.display_order, MenuModifier.name).offset(skip).limit(limit).all()
        return items, total

    def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(MenuModifier.id).filter(MenuModifier.name == name)
        if exclude_id:
            q = q.filter(MenuModifier.id != exclude_id)
        return q.first() is not None

    def get_by_ids(self, ids: list[int]) -> list[MenuModifier]:
        if not ids:
            return []
        return self.db.query(MenuModifier).filter(MenuModifier.id.in_(ids)).all()

    def replace_options(self, modifier: MenuModifier, options_data: list[dict]) -> None:
        """Replace all options for a modifier."""
        self.db.query(MenuModifierOption).filter(
            MenuModifierOption.modifier_id == modifier.id
        ).delete(synchronize_session=False)
        for opt in options_data:
            self.db.add(MenuModifierOption(modifier_id=modifier.id, **opt))
        self.db.flush()


# ---------------------------------------------------------------------------
# RestaurantTable
# ---------------------------------------------------------------------------
class RestaurantTableRepository(BaseRepository[RestaurantTable]):
    def __init__(self, db: Session) -> None:
        super().__init__(RestaurantTable, db)

    def list_active(
        self,
        skip: int = 0,
        limit: int = 200,
        search: Optional[str] = None,
        section: Optional[str] = None,
        location_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> tuple[list[RestaurantTable], int]:
        q = self.db.query(RestaurantTable).filter(RestaurantTable.is_active.is_(True))
        if search:
            q = q.filter(RestaurantTable.table_number.ilike(f"%{search}%"))
        if section:
            q = q.filter(RestaurantTable.section == section)
        if location_type:
            q = q.filter(RestaurantTable.location_type == location_type)
        if status:
            q = q.filter(RestaurantTable.status == status)
        total = q.count()
        items = q.order_by(RestaurantTable.table_number).offset(skip).limit(limit).all()
        return items, total

    def table_number_exists(self, table_number: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(RestaurantTable.id).filter(
            RestaurantTable.table_number == table_number,
            RestaurantTable.is_active.is_(True),
        )
        if exclude_id:
            q = q.filter(RestaurantTable.id != exclude_id)
        return q.first() is not None

    def count_by_status(self) -> dict[str, int]:
        rows = (
            self.db.query(RestaurantTable.status, RestaurantTable.id)
            .filter(RestaurantTable.is_active.is_(True))
            .all()
        )
        result: dict[str, int] = {}
        for row in rows:
            result[row.status] = result.get(row.status, 0) + 1
        return result
