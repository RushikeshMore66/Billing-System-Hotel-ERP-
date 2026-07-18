"""
Restaurant configuration router for NiralayOS — /api/v1/restaurant/*

Endpoints:
    GET/POST/PATCH/DELETE  /restaurant/categories
    GET/POST/PATCH/DELETE  /restaurant/menu-categories
    GET/POST/PATCH/DELETE  /restaurant/kitchen-stations
    GET/POST/PATCH/DELETE  /restaurant/menu-items
    GET/POST/PATCH/DELETE  /restaurant/modifiers
    GET/POST/PATCH/DELETE  /restaurant/tables
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db, require_permission
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.base import PaginatedResponse, SuccessResponse
from app.schemas.restaurant import (
    KitchenStationCreate,
    KitchenStationOut,
    KitchenStationUpdate,
    MenuCategoryCreate,
    MenuCategoryOut,
    MenuCategoryUpdate,
    MenuItemCreate,
    MenuItemOut,
    MenuItemUpdate,
    MenuModifierCreate,
    MenuModifierOut,
    MenuModifierUpdate,
    RestaurantCategoryCreate,
    RestaurantCategoryOut,
    RestaurantCategoryUpdate,
    RestaurantTableCreate,
    RestaurantTableOut,
    RestaurantTableUpdate,
)
from app.services.restaurant_config import (
    KitchenStationService,
    MenuCategoryService,
    MenuItemService,
    MenuModifierService,
    RestaurantCategoryService,
    RestaurantTableService,
)

router = APIRouter(prefix="/restaurant", tags=["Restaurant Configuration"])


# ===========================================================================
# Restaurant Categories
# ===========================================================================
@router.get(
    "/categories",
    response_model=PaginatedResponse[RestaurantCategoryOut],
    summary="List restaurant categories",
)
def list_restaurant_categories(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("restaurant:config:view")),
) -> PaginatedResponse[RestaurantCategoryOut]:
    items, total = RestaurantCategoryService(db).list(skip=(page - 1) * size, limit=size, search=search)
    return PaginatedResponse.build(items=[RestaurantCategoryOut.model_validate(c) for c in items], total=total, page=page, size=size)


@router.post(
    "/categories",
    response_model=SuccessResponse[RestaurantCategoryOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create restaurant category",
)
def create_restaurant_category(
    body: RestaurantCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("restaurant:config:manage")),
) -> SuccessResponse[RestaurantCategoryOut]:
    cat = RestaurantCategoryService(db).create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=RestaurantCategoryOut.model_validate(cat), message="Category created")


@router.patch(
    "/categories/{cat_id}",
    response_model=SuccessResponse[RestaurantCategoryOut],
    summary="Update restaurant category",
)
def update_restaurant_category(
    cat_id: int,
    body: RestaurantCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("restaurant:config:manage")),
) -> SuccessResponse[RestaurantCategoryOut]:
    cat = RestaurantCategoryService(db).update(cat_id, body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=RestaurantCategoryOut.model_validate(cat), message="Category updated")


@router.delete(
    "/categories/{cat_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete restaurant category",
)
def delete_restaurant_category(
    cat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("restaurant:config:manage")),
) -> SuccessResponse[MessageResponse]:
    RestaurantCategoryService(db).delete(cat_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="Category deleted"))


# ===========================================================================
# Menu Categories
# ===========================================================================
@router.get(
    "/menu-categories",
    response_model=PaginatedResponse[MenuCategoryOut],
    summary="List menu categories",
)
def list_menu_categories(
    page: int = Query(1, ge=1),
    size: int = Query(200, ge=1, le=500),
    search: str | None = Query(None),
    restaurant_category_id: int | None = Query(None),
    parent_id: int | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("restaurant:config:view")),
) -> PaginatedResponse[MenuCategoryOut]:
    items, total = MenuCategoryService(db).list(
        skip=(page - 1) * size, limit=size, search=search,
        restaurant_category_id=restaurant_category_id, parent_id=parent_id,
    )
    return PaginatedResponse.build(items=[MenuCategoryOut.model_validate(c) for c in items], total=total, page=page, size=size)


@router.post(
    "/menu-categories",
    response_model=SuccessResponse[MenuCategoryOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create menu category",
)
def create_menu_category(
    body: MenuCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("restaurant:config:manage")),
) -> SuccessResponse[MenuCategoryOut]:
    cat = MenuCategoryService(db).create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=MenuCategoryOut.model_validate(cat), message="Menu category created")


@router.patch(
    "/menu-categories/{cat_id}",
    response_model=SuccessResponse[MenuCategoryOut],
    summary="Update menu category",
)
def update_menu_category(
    cat_id: int,
    body: MenuCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("restaurant:config:manage")),
) -> SuccessResponse[MenuCategoryOut]:
    cat = MenuCategoryService(db).update(cat_id, body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=MenuCategoryOut.model_validate(cat), message="Menu category updated")


@router.delete(
    "/menu-categories/{cat_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete menu category",
)
def delete_menu_category(
    cat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("restaurant:config:manage")),
) -> SuccessResponse[MessageResponse]:
    MenuCategoryService(db).delete(cat_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="Menu category deleted"))


# ===========================================================================
# Kitchen Stations
# ===========================================================================
@router.get(
    "/kitchen-stations",
    response_model=PaginatedResponse[KitchenStationOut],
    summary="List kitchen stations",
)
def list_kitchen_stations(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("restaurant:config:view")),
) -> PaginatedResponse[KitchenStationOut]:
    items, total = KitchenStationService(db).list(skip=(page - 1) * size, limit=size, search=search)
    return PaginatedResponse.build(items=[KitchenStationOut.model_validate(s) for s in items], total=total, page=page, size=size)


@router.post(
    "/kitchen-stations",
    response_model=SuccessResponse[KitchenStationOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create kitchen station",
)
def create_kitchen_station(
    body: KitchenStationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("restaurant:config:manage")),
) -> SuccessResponse[KitchenStationOut]:
    s = KitchenStationService(db).create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=KitchenStationOut.model_validate(s), message="Kitchen station created")


@router.patch(
    "/kitchen-stations/{station_id}",
    response_model=SuccessResponse[KitchenStationOut],
    summary="Update kitchen station",
)
def update_kitchen_station(
    station_id: int,
    body: KitchenStationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("restaurant:config:manage")),
) -> SuccessResponse[KitchenStationOut]:
    s = KitchenStationService(db).update(station_id, body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=KitchenStationOut.model_validate(s), message="Kitchen station updated")


@router.delete(
    "/kitchen-stations/{station_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete kitchen station",
)
def delete_kitchen_station(
    station_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("restaurant:config:manage")),
) -> SuccessResponse[MessageResponse]:
    KitchenStationService(db).delete(station_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="Kitchen station deleted"))


# ===========================================================================
# Menu Items
# ===========================================================================
@router.get(
    "/menu-items",
    response_model=PaginatedResponse[MenuItemOut],
    summary="List menu items",
)
def list_menu_items(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=500),
    search: str | None = Query(None),
    menu_category_id: int | None = Query(None),
    kitchen_station_id: int | None = Query(None),
    food_type: str | None = Query(None),
    is_available: bool | None = Query(None),
    sort_by: str = Query("name"),
    sort_dir: str = Query("asc", pattern=r"^(asc|desc)$"),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("restaurant:config:view")),
) -> PaginatedResponse[MenuItemOut]:
    items, total = MenuItemService(db).list(
        skip=(page - 1) * size, limit=size, search=search,
        menu_category_id=menu_category_id,
        kitchen_station_id=kitchen_station_id,
        food_type=food_type, is_available=is_available,
        sort_by=sort_by, sort_dir=sort_dir,
    )
    return PaginatedResponse.build(items=[MenuItemOut.model_validate(i) for i in items], total=total, page=page, size=size)


@router.post(
    "/menu-items",
    response_model=SuccessResponse[MenuItemOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create menu item",
)
def create_menu_item(
    body: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("restaurant:config:manage")),
) -> SuccessResponse[MenuItemOut]:
    item = MenuItemService(db).create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=MenuItemOut.model_validate(item), message="Menu item created")


@router.patch(
    "/menu-items/{item_id}",
    response_model=SuccessResponse[MenuItemOut],
    summary="Update menu item",
)
def update_menu_item(
    item_id: int,
    body: MenuItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("restaurant:config:manage")),
) -> SuccessResponse[MenuItemOut]:
    item = MenuItemService(db).update(item_id, body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=MenuItemOut.model_validate(item), message="Menu item updated")


@router.delete(
    "/menu-items/{item_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete menu item",
)
def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("restaurant:config:manage")),
) -> SuccessResponse[MessageResponse]:
    MenuItemService(db).delete(item_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="Menu item deleted"))


# ===========================================================================
# Menu Modifiers
# ===========================================================================
@router.get(
    "/modifiers",
    response_model=PaginatedResponse[MenuModifierOut],
    summary="List menu modifiers",
)
def list_modifiers(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    search: str | None = Query(None),
    modifier_type: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("restaurant:config:view")),
) -> PaginatedResponse[MenuModifierOut]:
    items, total = MenuModifierService(db).list(skip=(page - 1) * size, limit=size, search=search, modifier_type=modifier_type)
    return PaginatedResponse.build(items=[MenuModifierOut.model_validate(m) for m in items], total=total, page=page, size=size)


@router.post(
    "/modifiers",
    response_model=SuccessResponse[MenuModifierOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create menu modifier",
)
def create_modifier(
    body: MenuModifierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("restaurant:config:manage")),
) -> SuccessResponse[MenuModifierOut]:
    m = MenuModifierService(db).create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=MenuModifierOut.model_validate(m), message="Modifier created")


@router.patch(
    "/modifiers/{modifier_id}",
    response_model=SuccessResponse[MenuModifierOut],
    summary="Update menu modifier",
)
def update_modifier(
    modifier_id: int,
    body: MenuModifierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("restaurant:config:manage")),
) -> SuccessResponse[MenuModifierOut]:
    m = MenuModifierService(db).update(modifier_id, body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=MenuModifierOut.model_validate(m), message="Modifier updated")


@router.delete(
    "/modifiers/{modifier_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete menu modifier",
)
def delete_modifier(
    modifier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("restaurant:config:manage")),
) -> SuccessResponse[MessageResponse]:
    MenuModifierService(db).delete(modifier_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="Modifier deleted"))


# ===========================================================================
# Restaurant Tables
# ===========================================================================
@router.get(
    "/tables",
    response_model=PaginatedResponse[RestaurantTableOut],
    summary="List restaurant tables",
)
def list_tables(
    page: int = Query(1, ge=1),
    size: int = Query(200, ge=1, le=500),
    search: str | None = Query(None),
    section: str | None = Query(None),
    location_type: str | None = Query(None),
    table_status: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("restaurant:config:view")),
) -> PaginatedResponse[RestaurantTableOut]:
    items, total = RestaurantTableService(db).list(
        skip=(page - 1) * size, limit=size, search=search,
        section=section, location_type=location_type, table_status=table_status,
    )
    return PaginatedResponse.build(items=[RestaurantTableOut.model_validate(t) for t in items], total=total, page=page, size=size)


@router.get(
    "/tables/status-summary",
    response_model=SuccessResponse[dict],
    summary="Table status summary counts",
)
def table_status_summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("restaurant:config:view")),
) -> SuccessResponse[dict]:
    return SuccessResponse.of(data=RestaurantTableService(db).count_by_status())


@router.post(
    "/tables",
    response_model=SuccessResponse[RestaurantTableOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create restaurant table",
)
def create_table(
    body: RestaurantTableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("restaurant:config:manage")),
) -> SuccessResponse[RestaurantTableOut]:
    t = RestaurantTableService(db).create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=RestaurantTableOut.model_validate(t), message="Table created")


@router.patch(
    "/tables/{table_id}",
    response_model=SuccessResponse[RestaurantTableOut],
    summary="Update restaurant table",
)
def update_table(
    table_id: int,
    body: RestaurantTableUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("restaurant:config:manage")),
) -> SuccessResponse[RestaurantTableOut]:
    t = RestaurantTableService(db).update(table_id, body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=RestaurantTableOut.model_validate(t), message="Table updated")


@router.delete(
    "/tables/{table_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete restaurant table",
)
def delete_table(
    table_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("restaurant:config:manage")),
) -> SuccessResponse[MessageResponse]:
    RestaurantTableService(db).delete(table_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="Table deleted"))
