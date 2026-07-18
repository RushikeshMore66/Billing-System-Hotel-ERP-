"""
Restaurant configuration service for NiralayOS.

Business validation:
  - Duplicate table numbers
  - Duplicate item codes
  - Modifier selection range validation
  - Item code uniqueness
"""

from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.restaurant import (
    KitchenStation,
    MenuCategory,
    MenuItem,
    MenuModifier,
    RestaurantCategory,
    RestaurantTable,
)
from app.repositories.restaurant import (
    KitchenStationRepository,
    MenuCategoryRepository,
    MenuItemRepository,
    MenuModifierRepository,
    RestaurantCategoryRepository,
    RestaurantTableRepository,
)
from app.schemas.restaurant import (
    KitchenStationCreate,
    KitchenStationUpdate,
    MenuCategoryCreate,
    MenuCategoryUpdate,
    MenuItemCreate,
    MenuItemUpdate,
    MenuModifierCreate,
    MenuModifierUpdate,
    RestaurantCategoryCreate,
    RestaurantCategoryUpdate,
    RestaurantTableCreate,
    RestaurantTableUpdate,
)


# ===========================================================================
# RestaurantCategoryService
# ===========================================================================
class RestaurantCategoryService:
    def __init__(self, db: Session) -> None:
        self._repo = RestaurantCategoryRepository(db)

    def list(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> tuple[list[RestaurantCategory], int]:
        return self._repo.list_active(skip=skip, limit=limit, search=search)

    def get_by_id(self, cat_id: int) -> RestaurantCategory:
        c = self._repo.get_by_id(cat_id)
        if not c or not c.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant category not found.")
        return c

    def create(self, data: RestaurantCategoryCreate, created_by: Optional[str] = None) -> RestaurantCategory:
        if self._repo.name_exists(data.name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category name already exists.")
        cat = RestaurantCategory(**data.model_dump(), created_by=created_by)
        return self._repo.create(cat)

    def update(self, cat_id: int, data: RestaurantCategoryUpdate, updated_by: Optional[str] = None) -> RestaurantCategory:
        cat = self.get_by_id(cat_id)
        if data.name is not None and data.name != cat.name:
            if self._repo.name_exists(data.name, exclude_id=cat_id):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category name already exists.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(cat, field, value)
        cat.updated_by = updated_by
        return self._repo.save(cat)

    def delete(self, cat_id: int, deleted_by: Optional[str] = None) -> None:
        cat = self.get_by_id(cat_id)
        cat.soft_delete(deleted_by=deleted_by)
        self._repo.save(cat)


# ===========================================================================
# MenuCategoryService
# ===========================================================================
class MenuCategoryService:
    def __init__(self, db: Session) -> None:
        self._repo = MenuCategoryRepository(db)

    def list(
        self,
        skip: int = 0,
        limit: int = 200,
        search: Optional[str] = None,
        restaurant_category_id: Optional[int] = None,
        parent_id: Optional[int] = None,
    ) -> tuple[list[MenuCategory], int]:
        return self._repo.list_active(
            skip=skip, limit=limit, search=search,
            restaurant_category_id=restaurant_category_id,
            parent_id=parent_id,
        )

    def get_by_id(self, cat_id: int) -> MenuCategory:
        c = self._repo.get_by_id(cat_id)
        if not c or not c.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu category not found.")
        return c

    def create(self, data: MenuCategoryCreate, created_by: Optional[str] = None) -> MenuCategory:
        if data.parent_id is not None:
            parent = self._repo.get_by_id(data.parent_id)
            if not parent or not parent.is_active:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent category not found.")
        cat = MenuCategory(**data.model_dump(), created_by=created_by)
        return self._repo.create(cat)

    def update(self, cat_id: int, data: MenuCategoryUpdate, updated_by: Optional[str] = None) -> MenuCategory:
        cat = self.get_by_id(cat_id)
        if data.parent_id is not None:
            if data.parent_id == cat_id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="A category cannot be its own parent.",
                )
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(cat, field, value)
        cat.updated_by = updated_by
        return self._repo.save(cat)

    def delete(self, cat_id: int, deleted_by: Optional[str] = None) -> None:
        cat = self.get_by_id(cat_id)
        cat.soft_delete(deleted_by=deleted_by)
        self._repo.save(cat)


# ===========================================================================
# KitchenStationService
# ===========================================================================
class KitchenStationService:
    def __init__(self, db: Session) -> None:
        self._repo = KitchenStationRepository(db)

    def list(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> tuple[list[KitchenStation], int]:
        return self._repo.list_active(skip=skip, limit=limit, search=search)

    def get_by_id(self, station_id: int) -> KitchenStation:
        s = self._repo.get_by_id(station_id)
        if not s or not s.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kitchen station not found.")
        return s

    def create(self, data: KitchenStationCreate, created_by: Optional[str] = None) -> KitchenStation:
        if self._repo.name_exists(data.name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Station name already exists.")
        s = KitchenStation(**data.model_dump(), created_by=created_by)
        return self._repo.create(s)

    def update(self, station_id: int, data: KitchenStationUpdate, updated_by: Optional[str] = None) -> KitchenStation:
        s = self.get_by_id(station_id)
        if data.name is not None and data.name != s.name:
            if self._repo.name_exists(data.name, exclude_id=station_id):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Station name already exists.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(s, field, value)
        s.updated_by = updated_by
        return self._repo.save(s)

    def delete(self, station_id: int, deleted_by: Optional[str] = None) -> None:
        s = self.get_by_id(station_id)
        s.soft_delete(deleted_by=deleted_by)
        self._repo.save(s)


# ===========================================================================
# MenuItemService
# ===========================================================================
class MenuItemService:
    def __init__(self, db: Session) -> None:
        self._repo = MenuItemRepository(db)
        self._modifier_repo = MenuModifierRepository(db)

    def list(
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
        return self._repo.list_active(
            skip=skip, limit=limit, search=search,
            menu_category_id=menu_category_id,
            kitchen_station_id=kitchen_station_id,
            food_type=food_type,
            is_available=is_available,
            sort_by=sort_by, sort_dir=sort_dir,
        )

    def get_by_id(self, item_id: int) -> MenuItem:
        item = self._repo.get_by_id(item_id)
        if not item or not item.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found.")
        return item

    def create(self, data: MenuItemCreate, created_by: Optional[str] = None) -> MenuItem:
        if self._repo.item_code_exists(data.item_code):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Item code '{data.item_code}' already exists.",
            )
        modifiers = self._modifier_repo.get_by_ids(data.modifier_ids)
        payload = data.model_dump(exclude={"modifier_ids"})
        item = MenuItem(**payload, modifiers=modifiers, created_by=created_by)
        return self._repo.create(item)

    def update(self, item_id: int, data: MenuItemUpdate, updated_by: Optional[str] = None) -> MenuItem:
        item = self.get_by_id(item_id)
        if data.modifier_ids is not None:
            item.modifiers = self._modifier_repo.get_by_ids(data.modifier_ids)
        for field, value in data.model_dump(exclude={"modifier_ids"}, exclude_none=True).items():
            setattr(item, field, value)
        item.updated_by = updated_by
        return self._repo.save(item)

    def delete(self, item_id: int, deleted_by: Optional[str] = None) -> None:
        item = self.get_by_id(item_id)
        item.soft_delete(deleted_by=deleted_by)
        self._repo.save(item)


# ===========================================================================
# MenuModifierService
# ===========================================================================
class MenuModifierService:
    def __init__(self, db: Session) -> None:
        self._repo = MenuModifierRepository(db)

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        modifier_type: Optional[str] = None,
    ) -> tuple[list[MenuModifier], int]:
        return self._repo.list_active(skip=skip, limit=limit, search=search, modifier_type=modifier_type)

    def get_by_id(self, modifier_id: int) -> MenuModifier:
        m = self._repo.get_by_id(modifier_id)
        if not m or not m.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modifier not found.")
        return m

    def create(self, data: MenuModifierCreate, created_by: Optional[str] = None) -> MenuModifier:
        if self._repo.name_exists(data.name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Modifier name already exists.")
        self._validate_selections(data.min_selections, data.max_selections)
        payload = data.model_dump(exclude={"options"})
        m = MenuModifier(**payload, created_by=created_by)
        self._repo.create(m)
        if data.options:
            self._repo.replace_options(m, [opt.model_dump() for opt in data.options])
        return self._repo.get_by_id(m.id)  # type: ignore[return-value]

    def update(self, modifier_id: int, data: MenuModifierUpdate, updated_by: Optional[str] = None) -> MenuModifier:
        m = self.get_by_id(modifier_id)
        if data.name is not None and data.name != m.name:
            if self._repo.name_exists(data.name, exclude_id=modifier_id):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Modifier name already exists.")
        min_s = data.min_selections if data.min_selections is not None else m.min_selections
        max_s = data.max_selections if data.max_selections is not None else m.max_selections
        self._validate_selections(min_s, max_s)
        if data.options is not None:
            self._repo.replace_options(m, [opt.model_dump() for opt in data.options])
        for field, value in data.model_dump(exclude={"options"}, exclude_none=True).items():
            setattr(m, field, value)
        m.updated_by = updated_by
        return self._repo.save(m)

    def delete(self, modifier_id: int, deleted_by: Optional[str] = None) -> None:
        m = self.get_by_id(modifier_id)
        m.soft_delete(deleted_by=deleted_by)
        self._repo.save(m)

    @staticmethod
    def _validate_selections(min_s: int, max_s: Optional[int]) -> None:
        if max_s is not None and max_s < min_s:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="max_selections must be >= min_selections.",
            )


# ===========================================================================
# RestaurantTableService
# ===========================================================================
class RestaurantTableService:
    def __init__(self, db: Session) -> None:
        self._repo = RestaurantTableRepository(db)

    def list(
        self,
        skip: int = 0,
        limit: int = 200,
        search: Optional[str] = None,
        section: Optional[str] = None,
        location_type: Optional[str] = None,
        table_status: Optional[str] = None,
    ) -> tuple[list[RestaurantTable], int]:
        return self._repo.list_active(
            skip=skip, limit=limit, search=search,
            section=section, location_type=location_type, status=table_status,
        )

    def get_by_id(self, table_id: int) -> RestaurantTable:
        t = self._repo.get_by_id(table_id)
        if not t or not t.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found.")
        return t

    def create(self, data: RestaurantTableCreate, created_by: Optional[str] = None) -> RestaurantTable:
        if self._repo.table_number_exists(data.table_number):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Table number '{data.table_number}' already exists.",
            )
        t = RestaurantTable(**data.model_dump(), created_by=created_by)
        return self._repo.create(t)

    def update(self, table_id: int, data: RestaurantTableUpdate, updated_by: Optional[str] = None) -> RestaurantTable:
        t = self.get_by_id(table_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(t, field, value)
        t.updated_by = updated_by
        return self._repo.save(t)

    def delete(self, table_id: int, deleted_by: Optional[str] = None) -> None:
        t = self.get_by_id(table_id)
        t.soft_delete(deleted_by=deleted_by)
        self._repo.save(t)

    def count_by_status(self) -> dict[str, int]:
        return self._repo.count_by_status()
