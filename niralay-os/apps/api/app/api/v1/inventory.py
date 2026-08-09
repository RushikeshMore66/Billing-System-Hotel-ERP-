"""
Inventory Router for NiralayOS.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.schemas.base import PaginatedResponse, SuccessResponse
from app.schemas.inventory import (
    InventoryCategoryCreate,
    InventoryCategoryOut,
    InventoryCategoryUpdate,
    InventoryItemCreate,
    InventoryItemOut,
    InventoryItemUpdate,
    StockLevelSummary,
    StockMovementCreate,
    StockMovementOut,
    StoreLocationCreate,
    StoreLocationOut,
    StoreLocationUpdate,
)
from app.services.inventory import (
    InventoryCategoryService,
    InventoryItemService,
    StoreLocationService,
)

router = APIRouter(prefix="/inventory", tags=["Inventory"])


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------
@router.get("/categories", response_model=SuccessResponse[list[InventoryCategoryOut]])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[list[InventoryCategoryOut]]:
    svc = InventoryCategoryService(db)
    return SuccessResponse.of(data=svc.list_all())


@router.post(
    "/categories",
    response_model=SuccessResponse[InventoryCategoryOut],
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    data: InventoryCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[InventoryCategoryOut]:
    svc = InventoryCategoryService(db)
    return SuccessResponse.of(data=svc.create(data), message="Category created successfully")


@router.get("/categories/{category_id}", response_model=SuccessResponse[InventoryCategoryOut])
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[InventoryCategoryOut]:
    svc = InventoryCategoryService(db)
    return SuccessResponse.of(data=svc.get(category_id))


@router.patch("/categories/{category_id}", response_model=SuccessResponse[InventoryCategoryOut])
def update_category(
    category_id: int,
    data: InventoryCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[InventoryCategoryOut]:
    svc = InventoryCategoryService(db)
    return SuccessResponse.of(data=svc.update(category_id, data), message="Category updated")


@router.delete("/categories/{category_id}", response_model=SuccessResponse[None])
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[None]:
    svc = InventoryCategoryService(db)
    svc.delete(category_id)
    return SuccessResponse.of(data=None, message="Category deleted")


# ---------------------------------------------------------------------------
# Store Locations
# ---------------------------------------------------------------------------
@router.get("/locations", response_model=SuccessResponse[list[StoreLocationOut]])
def list_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[list[StoreLocationOut]]:
    svc = StoreLocationService(db)
    return SuccessResponse.of(data=svc.list_all())


@router.post(
    "/locations",
    response_model=SuccessResponse[StoreLocationOut],
    status_code=status.HTTP_201_CREATED,
)
def create_location(
    data: StoreLocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[StoreLocationOut]:
    svc = StoreLocationService(db)
    return SuccessResponse.of(data=svc.create(data), message="Location created successfully")


@router.patch("/locations/{location_id}", response_model=SuccessResponse[StoreLocationOut])
def update_location(
    location_id: int,
    data: StoreLocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[StoreLocationOut]:
    svc = StoreLocationService(db)
    return SuccessResponse.of(data=svc.update(location_id, data), message="Location updated")


@router.delete("/locations/{location_id}", response_model=SuccessResponse[None])
def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[None]:
    svc = StoreLocationService(db)
    svc.delete(location_id)
    return SuccessResponse.of(data=None, message="Location deleted")


# ---------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------
@router.get("/items", response_model=PaginatedResponse[InventoryItemOut])
def list_items(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    location_id: Optional[int] = None,
    item_type: Optional[str] = None,
    stock_level: Optional[str] = Query(None, description="ok | low | critical"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PaginatedResponse[InventoryItemOut]:
    svc = InventoryItemService(db)
    skip = (page - 1) * size
    items, total = svc.search(
        query=search,
        category_id=category_id,
        location_id=location_id,
        item_type=item_type,
        stock_level=stock_level,
        skip=skip,
        limit=size,
    )
    return PaginatedResponse.of(items=items, total=total, page=page, size=size)


@router.post(
    "/items",
    response_model=SuccessResponse[InventoryItemOut],
    status_code=status.HTTP_201_CREATED,
)
def create_item(
    data: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[InventoryItemOut]:
    svc = InventoryItemService(db)
    item = svc.create(data, recorded_by=str(current_user.uuid))
    return SuccessResponse.of(data=item, message="Inventory item created successfully")


@router.get("/items/alerts", response_model=SuccessResponse[list[InventoryItemOut]])
def get_low_stock_alerts(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[list[InventoryItemOut]]:
    svc = InventoryItemService(db)
    return SuccessResponse.of(data=svc.get_low_stock_items(limit=limit))


@router.get("/items/{item_id}", response_model=SuccessResponse[InventoryItemOut])
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[InventoryItemOut]:
    svc = InventoryItemService(db)
    return SuccessResponse.of(data=svc.get(item_id))


@router.patch("/items/{item_id}", response_model=SuccessResponse[InventoryItemOut])
def update_item(
    item_id: int,
    data: InventoryItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[InventoryItemOut]:
    svc = InventoryItemService(db)
    return SuccessResponse.of(data=svc.update(item_id, data), message="Item updated")


@router.delete("/items/{item_id}", response_model=SuccessResponse[None])
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[None]:
    svc = InventoryItemService(db)
    svc.delete(item_id)
    return SuccessResponse.of(data=None, message="Item deleted")


# ---------------------------------------------------------------------------
# Stock Movements
# ---------------------------------------------------------------------------
@router.post(
    "/items/{item_id}/movements",
    response_model=SuccessResponse[StockMovementOut],
    status_code=status.HTTP_201_CREATED,
)
def record_movement(
    item_id: int,
    data: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[StockMovementOut]:
    data.item_id = item_id  # Ensure path param takes precedence
    svc = InventoryItemService(db)
    movement = svc.record_movement(data, recorded_by=str(current_user.uuid))
    return SuccessResponse.of(data=movement, message="Stock movement recorded")


@router.get(
    "/items/{item_id}/movements",
    response_model=PaginatedResponse[StockMovementOut],
)
def list_movements(
    item_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PaginatedResponse[StockMovementOut]:
    svc = InventoryItemService(db)
    skip = (page - 1) * size
    movements, total = svc.get_movements(item_id, skip=skip, limit=size)
    return PaginatedResponse.of(items=movements, total=total, page=page, size=size)
