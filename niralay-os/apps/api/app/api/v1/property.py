"""
Property configuration router for NiralayOS — /api/v1/property/*

Endpoints:
    GET/PATCH  /property/profile
    GET/POST/PATCH/DELETE  /property/floors
    GET/POST/PATCH/DELETE  /property/amenities
    GET/POST/PATCH/DELETE  /property/bed-types
    GET/POST/PATCH/DELETE  /property/room-types
    GET/POST/PATCH/DELETE  /property/rooms
    GET/POST/PATCH/DELETE  /property/taxes
    GET/POST/PATCH/DELETE  /property/payment-methods
    GET/POST/PATCH/DELETE  /property/currencies
    GET/POST/PATCH/DELETE  /property/seasons
    GET/POST/PATCH/DELETE  /property/rate-plans
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db, require_permission
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.base import PaginatedResponse, SuccessResponse
from app.schemas.property import (
    AmenityCreate,
    AmenityOut,
    AmenityUpdate,
    BedTypeCreate,
    BedTypeOut,
    BedTypeUpdate,
    CurrencyCreate,
    CurrencyOut,
    CurrencyUpdate,
    FloorCreate,
    FloorOut,
    FloorUpdate,
    PaymentMethodCreate,
    PaymentMethodOut,
    PaymentMethodUpdate,
    PropertyProfileOut,
    PropertyProfileUpdate,
    RatePlanCreate,
    RatePlanOut,
    RatePlanUpdate,
    RoomBulkCreate,
    RoomBulkResult,
    RoomCreate,
    RoomOut,
    RoomTypeCreate,
    RoomTypeOut,
    RoomTypeUpdate,
    RoomUpdate,
    SeasonCreate,
    SeasonOut,
    SeasonUpdate,
    TaxCreate,
    TaxOut,
    TaxUpdate,
)
from app.services.property import (
    AmenityService,
    BedTypeService,
    CurrencyService,
    FloorService,
    PaymentMethodService,
    PropertyProfileService,
    RatePlanService,
    RoomService,
    RoomTypeService,
    SeasonService,
    TaxService,
)

router = APIRouter(prefix="/property", tags=["Property Configuration"])


# ===========================================================================
# Property Profile
# ===========================================================================
@router.get(
    "/profile",
    response_model=SuccessResponse[PropertyProfileOut],
    summary="Get property profile",
    description="Returns the singleton property profile. Creates a default one if it does not exist.",
)
def get_profile(
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("property:view")),
) -> SuccessResponse[PropertyProfileOut]:
    profile = PropertyProfileService(db).get()
    return SuccessResponse.of(data=PropertyProfileOut.model_validate(profile))


@router.patch(
    "/profile",
    response_model=SuccessResponse[PropertyProfileOut],
    summary="Update property profile",
)
def update_profile(
    body: PropertyProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:update")),
) -> SuccessResponse[PropertyProfileOut]:
    profile = PropertyProfileService(db).update(body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=PropertyProfileOut.model_validate(profile), message="Property profile updated")


# ===========================================================================
# Floors
# ===========================================================================
@router.get(
    "/floors",
    response_model=PaginatedResponse[FloorOut],
    summary="List floors",
)
def list_floors(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=500),
    search: str | None = Query(None),
    floor_status: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("property:view")),
) -> PaginatedResponse[FloorOut]:
    items, total = FloorService(db).list(skip=(page - 1) * size, limit=size, search=search, status=floor_status)
    return PaginatedResponse.build(items=[FloorOut.model_validate(f) for f in items], total=total, page=page, size=size)


@router.post(
    "/floors",
    response_model=SuccessResponse[FloorOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create floor",
)
def create_floor(
    body: FloorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:create")),
) -> SuccessResponse[FloorOut]:
    floor = FloorService(db).create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=FloorOut.model_validate(floor), message="Floor created")


@router.patch(
    "/floors/{floor_id}",
    response_model=SuccessResponse[FloorOut],
    summary="Update floor",
)
def update_floor(
    floor_id: int,
    body: FloorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:update")),
) -> SuccessResponse[FloorOut]:
    floor = FloorService(db).update(floor_id, body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=FloorOut.model_validate(floor), message="Floor updated")


@router.delete(
    "/floors/{floor_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete floor",
)
def delete_floor(
    floor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:delete")),
) -> SuccessResponse[MessageResponse]:
    FloorService(db).delete(floor_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="Floor deleted"))


# ===========================================================================
# Amenities
# ===========================================================================
@router.get(
    "/amenities",
    response_model=PaginatedResponse[AmenityOut],
    summary="List amenities",
)
def list_amenities(
    page: int = Query(1, ge=1),
    size: int = Query(200, ge=1, le=500),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("property:view")),
) -> PaginatedResponse[AmenityOut]:
    items, total = AmenityService(db).list(skip=(page - 1) * size, limit=size, search=search)
    return PaginatedResponse.build(items=[AmenityOut.model_validate(a) for a in items], total=total, page=page, size=size)


@router.post(
    "/amenities",
    response_model=SuccessResponse[AmenityOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create amenity",
)
def create_amenity(
    body: AmenityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:create")),
) -> SuccessResponse[AmenityOut]:
    amenity = AmenityService(db).create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=AmenityOut.model_validate(amenity), message="Amenity created")


@router.patch(
    "/amenities/{amenity_id}",
    response_model=SuccessResponse[AmenityOut],
    summary="Update amenity",
)
def update_amenity(
    amenity_id: int,
    body: AmenityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:update")),
) -> SuccessResponse[AmenityOut]:
    amenity = AmenityService(db).update(amenity_id, body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=AmenityOut.model_validate(amenity), message="Amenity updated")


@router.delete(
    "/amenities/{amenity_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete amenity",
)
def delete_amenity(
    amenity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:delete")),
) -> SuccessResponse[MessageResponse]:
    AmenityService(db).delete(amenity_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="Amenity deleted"))


# ===========================================================================
# Bed Types
# ===========================================================================
@router.get(
    "/bed-types",
    response_model=PaginatedResponse[BedTypeOut],
    summary="List bed types",
)
def list_bed_types(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("property:view")),
) -> PaginatedResponse[BedTypeOut]:
    items, total = BedTypeService(db).list(skip=(page - 1) * size, limit=size, search=search)
    return PaginatedResponse.build(items=[BedTypeOut.model_validate(b) for b in items], total=total, page=page, size=size)


@router.post(
    "/bed-types",
    response_model=SuccessResponse[BedTypeOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create bed type",
)
def create_bed_type(
    body: BedTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:create")),
) -> SuccessResponse[BedTypeOut]:
    bt = BedTypeService(db).create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=BedTypeOut.model_validate(bt), message="Bed type created")


@router.patch(
    "/bed-types/{bed_type_id}",
    response_model=SuccessResponse[BedTypeOut],
    summary="Update bed type",
)
def update_bed_type(
    bed_type_id: int,
    body: BedTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:update")),
) -> SuccessResponse[BedTypeOut]:
    bt = BedTypeService(db).update(bed_type_id, body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=BedTypeOut.model_validate(bt), message="Bed type updated")


@router.delete(
    "/bed-types/{bed_type_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete bed type",
)
def delete_bed_type(
    bed_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:delete")),
) -> SuccessResponse[MessageResponse]:
    BedTypeService(db).delete(bed_type_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="Bed type deleted"))


# ===========================================================================
# Room Types
# ===========================================================================
@router.get(
    "/room-types",
    response_model=PaginatedResponse[RoomTypeOut],
    summary="List room types",
)
def list_room_types(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    search: str | None = Query(None),
    rt_status: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("property:view")),
) -> PaginatedResponse[RoomTypeOut]:
    items, total = RoomTypeService(db).list(skip=(page - 1) * size, limit=size, search=search, status=rt_status)
    return PaginatedResponse.build(items=[RoomTypeOut.model_validate(r) for r in items], total=total, page=page, size=size)


@router.post(
    "/room-types",
    response_model=SuccessResponse[RoomTypeOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create room type",
)
def create_room_type(
    body: RoomTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:create")),
) -> SuccessResponse[RoomTypeOut]:
    rt = RoomTypeService(db).create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=RoomTypeOut.model_validate(rt), message="Room type created")


@router.patch(
    "/room-types/{room_type_id}",
    response_model=SuccessResponse[RoomTypeOut],
    summary="Update room type",
)
def update_room_type(
    room_type_id: int,
    body: RoomTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:update")),
) -> SuccessResponse[RoomTypeOut]:
    rt = RoomTypeService(db).update(room_type_id, body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=RoomTypeOut.model_validate(rt), message="Room type updated")


@router.delete(
    "/room-types/{room_type_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete room type",
)
def delete_room_type(
    room_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:delete")),
) -> SuccessResponse[MessageResponse]:
    RoomTypeService(db).delete(room_type_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="Room type deleted"))


# ===========================================================================
# Rooms
# ===========================================================================
@router.get(
    "/rooms",
    response_model=PaginatedResponse[RoomOut],
    summary="List rooms",
)
def list_rooms(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=500),
    search: str | None = Query(None),
    floor_id: int | None = Query(None),
    room_type_id: int | None = Query(None),
    room_status: str | None = Query(None, alias="status"),
    housekeeping_status: str | None = Query(None),
    maintenance_status: str | None = Query(None),
    sort_by: str = Query("room_number"),
    sort_dir: str = Query("asc", pattern=r"^(asc|desc)$"),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("property:view")),
) -> PaginatedResponse[RoomOut]:
    items, total = RoomService(db).list(
        skip=(page - 1) * size, limit=size, search=search,
        floor_id=floor_id, room_type_id=room_type_id,
        room_status=room_status,
        housekeeping_status=housekeeping_status,
        maintenance_status=maintenance_status,
        sort_by=sort_by, sort_dir=sort_dir,
    )
    return PaginatedResponse.build(items=[RoomOut.model_validate(r) for r in items], total=total, page=page, size=size)


@router.get(
    "/rooms/status-summary",
    response_model=SuccessResponse[dict],
    summary="Room status summary counts",
)
def room_status_summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("property:view")),
) -> SuccessResponse[dict]:
    counts = RoomService(db).count_by_status()
    return SuccessResponse.of(data=counts)


@router.post(
    "/rooms",
    response_model=SuccessResponse[RoomOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create room",
)
def create_room(
    body: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:create")),
) -> SuccessResponse[RoomOut]:
    room = RoomService(db).create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=RoomOut.model_validate(room), message="Room created")


@router.post(
    "/rooms/bulk",
    response_model=SuccessResponse[RoomBulkResult],
    status_code=status.HTTP_201_CREATED,
    summary="Bulk create rooms",
)
def bulk_create_rooms(
    body: RoomBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:create")),
) -> SuccessResponse[RoomBulkResult]:
    result = RoomService(db).bulk_create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=result, message=f"Bulk import complete: {result.created} created, {result.failed} failed")


@router.patch(
    "/rooms/{room_id}",
    response_model=SuccessResponse[RoomOut],
    summary="Update room",
)
def update_room(
    room_id: int,
    body: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:update")),
) -> SuccessResponse[RoomOut]:
    room = RoomService(db).update(room_id, body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=RoomOut.model_validate(room), message="Room updated")


@router.delete(
    "/rooms/{room_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete room",
)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:delete")),
) -> SuccessResponse[MessageResponse]:
    RoomService(db).delete(room_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="Room deleted"))


# ===========================================================================
# Taxes
# ===========================================================================
@router.get(
    "/taxes",
    response_model=PaginatedResponse[TaxOut],
    summary="List taxes",
)
def list_taxes(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    search: str | None = Query(None),
    applies_to: str | None = Query(None),
    tax_type: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("property:view")),
) -> PaginatedResponse[TaxOut]:
    items, total = TaxService(db).list(
        skip=(page - 1) * size, limit=size, search=search,
        applies_to=applies_to, tax_type=tax_type,
    )
    return PaginatedResponse.build(items=[TaxOut.model_validate(t) for t in items], total=total, page=page, size=size)


@router.post(
    "/taxes",
    response_model=SuccessResponse[TaxOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create tax",
)
def create_tax(
    body: TaxCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:create")),
) -> SuccessResponse[TaxOut]:
    tax = TaxService(db).create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=TaxOut.model_validate(tax), message="Tax created")


@router.patch(
    "/taxes/{tax_id}",
    response_model=SuccessResponse[TaxOut],
    summary="Update tax",
)
def update_tax(
    tax_id: int,
    body: TaxUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:update")),
) -> SuccessResponse[TaxOut]:
    tax = TaxService(db).update(tax_id, body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=TaxOut.model_validate(tax), message="Tax updated")


@router.delete(
    "/taxes/{tax_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete tax",
)
def delete_tax(
    tax_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:delete")),
) -> SuccessResponse[MessageResponse]:
    TaxService(db).delete(tax_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="Tax deleted"))


# ===========================================================================
# Payment Methods
# ===========================================================================
@router.get(
    "/payment-methods",
    response_model=PaginatedResponse[PaymentMethodOut],
    summary="List payment methods",
)
def list_payment_methods(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    search: str | None = Query(None),
    payment_type: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("property:view")),
) -> PaginatedResponse[PaymentMethodOut]:
    items, total = PaymentMethodService(db).list(skip=(page - 1) * size, limit=size, search=search, payment_type=payment_type)
    return PaginatedResponse.build(items=[PaymentMethodOut.model_validate(p) for p in items], total=total, page=page, size=size)


@router.post(
    "/payment-methods",
    response_model=SuccessResponse[PaymentMethodOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create payment method",
)
def create_payment_method(
    body: PaymentMethodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:create")),
) -> SuccessResponse[PaymentMethodOut]:
    pm = PaymentMethodService(db).create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=PaymentMethodOut.model_validate(pm), message="Payment method created")


@router.patch(
    "/payment-methods/{pm_id}",
    response_model=SuccessResponse[PaymentMethodOut],
    summary="Update payment method",
)
def update_payment_method(
    pm_id: int,
    body: PaymentMethodUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:update")),
) -> SuccessResponse[PaymentMethodOut]:
    pm = PaymentMethodService(db).update(pm_id, body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=PaymentMethodOut.model_validate(pm), message="Payment method updated")


@router.delete(
    "/payment-methods/{pm_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete payment method",
)
def delete_payment_method(
    pm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:delete")),
) -> SuccessResponse[MessageResponse]:
    PaymentMethodService(db).delete(pm_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="Payment method deleted"))


# ===========================================================================
# Currencies
# ===========================================================================
@router.get(
    "/currencies",
    response_model=PaginatedResponse[CurrencyOut],
    summary="List currencies",
)
def list_currencies(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("property:view")),
) -> PaginatedResponse[CurrencyOut]:
    items, total = CurrencyService(db).list(skip=(page - 1) * size, limit=size, search=search)
    return PaginatedResponse.build(items=[CurrencyOut.model_validate(c) for c in items], total=total, page=page, size=size)


@router.post(
    "/currencies",
    response_model=SuccessResponse[CurrencyOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create currency",
)
def create_currency(
    body: CurrencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:create")),
) -> SuccessResponse[CurrencyOut]:
    c = CurrencyService(db).create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=CurrencyOut.model_validate(c), message="Currency created")


@router.patch(
    "/currencies/{currency_id}",
    response_model=SuccessResponse[CurrencyOut],
    summary="Update currency",
)
def update_currency(
    currency_id: int,
    body: CurrencyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:update")),
) -> SuccessResponse[CurrencyOut]:
    c = CurrencyService(db).update(currency_id, body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=CurrencyOut.model_validate(c), message="Currency updated")


@router.delete(
    "/currencies/{currency_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete currency",
)
def delete_currency(
    currency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:delete")),
) -> SuccessResponse[MessageResponse]:
    CurrencyService(db).delete(currency_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="Currency deleted"))


# ===========================================================================
# Seasons
# ===========================================================================
@router.get(
    "/seasons",
    response_model=PaginatedResponse[SeasonOut],
    summary="List seasons",
)
def list_seasons(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("property:view")),
) -> PaginatedResponse[SeasonOut]:
    items, total = SeasonService(db).list(skip=(page - 1) * size, limit=size, search=search)
    return PaginatedResponse.build(items=[SeasonOut.model_validate(s) for s in items], total=total, page=page, size=size)


@router.post(
    "/seasons",
    response_model=SuccessResponse[SeasonOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create season",
)
def create_season(
    body: SeasonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:create")),
) -> SuccessResponse[SeasonOut]:
    s = SeasonService(db).create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=SeasonOut.model_validate(s), message="Season created")


@router.patch(
    "/seasons/{season_id}",
    response_model=SuccessResponse[SeasonOut],
    summary="Update season",
)
def update_season(
    season_id: int,
    body: SeasonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:update")),
) -> SuccessResponse[SeasonOut]:
    s = SeasonService(db).update(season_id, body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=SeasonOut.model_validate(s), message="Season updated")


@router.delete(
    "/seasons/{season_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete season",
)
def delete_season(
    season_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:delete")),
) -> SuccessResponse[MessageResponse]:
    SeasonService(db).delete(season_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="Season deleted"))


# ===========================================================================
# Rate Plans
# ===========================================================================
@router.get(
    "/rate-plans",
    response_model=PaginatedResponse[RatePlanOut],
    summary="List rate plans",
)
def list_rate_plans(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    search: str | None = Query(None),
    meal_plan: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("property:view")),
) -> PaginatedResponse[RatePlanOut]:
    items, total = RatePlanService(db).list(skip=(page - 1) * size, limit=size, search=search, meal_plan=meal_plan)
    return PaginatedResponse.build(items=[RatePlanOut.model_validate(r) for r in items], total=total, page=page, size=size)


@router.post(
    "/rate-plans",
    response_model=SuccessResponse[RatePlanOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create rate plan",
)
def create_rate_plan(
    body: RatePlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:create")),
) -> SuccessResponse[RatePlanOut]:
    rp = RatePlanService(db).create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=RatePlanOut.model_validate(rp), message="Rate plan created")


@router.patch(
    "/rate-plans/{rate_plan_id}",
    response_model=SuccessResponse[RatePlanOut],
    summary="Update rate plan",
)
def update_rate_plan(
    rate_plan_id: int,
    body: RatePlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:update")),
) -> SuccessResponse[RatePlanOut]:
    rp = RatePlanService(db).update(rate_plan_id, body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=RatePlanOut.model_validate(rp), message="Rate plan updated")


@router.delete(
    "/rate-plans/{rate_plan_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete rate plan",
)
def delete_rate_plan(
    rate_plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("property:delete")),
) -> SuccessResponse[MessageResponse]:
    RatePlanService(db).delete(rate_plan_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="Rate plan deleted"))
