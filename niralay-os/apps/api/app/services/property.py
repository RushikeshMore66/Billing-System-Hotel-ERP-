"""
Property configuration service for NiralayOS.

Business validation lives here:
  - Duplicate room numbers
  - Duplicate floor numbers
  - Season date overlap
  - Rate plan pricing validation
  - Room type amenity linking
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.property import (
    Amenity,
    BedType,
    Currency,
    Floor,
    PaymentMethod,
    PropertyProfile,
    RatePlan,
    Room,
    RoomType,
    RoomTypeImage,
    Season,
    Tax,
)
from app.repositories.property import (
    AmenityRepository,
    BedTypeRepository,
    CurrencyRepository,
    FloorRepository,
    PaymentMethodRepository,
    PropertyProfileRepository,
    RatePlanRepository,
    RoomRepository,
    RoomTypeRepository,
    SeasonRepository,
    TaxRepository,
)
from app.schemas.property import (
    AmenityCreate,
    AmenityUpdate,
    BedTypeCreate,
    BedTypeUpdate,
    CurrencyCreate,
    CurrencyUpdate,
    FloorCreate,
    FloorUpdate,
    PaymentMethodCreate,
    PaymentMethodUpdate,
    PropertyProfileUpdate,
    RatePlanCreate,
    RatePlanUpdate,
    RoomBulkCreate,
    RoomBulkResult,
    RoomCreate,
    RoomTypeCreate,
    RoomTypeUpdate,
    RoomUpdate,
    SeasonCreate,
    SeasonUpdate,
    TaxCreate,
    TaxUpdate,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ===========================================================================
# PropertyProfileService
# ===========================================================================
class PropertyProfileService:
    def __init__(self, db: Session) -> None:
        self._repo = PropertyProfileRepository(db)

    def get(self) -> PropertyProfile:
        return self._repo.get_or_create()

    def update(self, data: PropertyProfileUpdate, updated_by: Optional[str] = None) -> PropertyProfile:
        profile = self._repo.get_or_create()
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(profile, field, value)
        profile.updated_by = updated_by
        return self._repo.save(profile)


# ===========================================================================
# FloorService
# ===========================================================================
class FloorService:
    def __init__(self, db: Session) -> None:
        self._repo = FloorRepository(db)

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> tuple[list[Floor], int]:
        return self._repo.list_active(skip=skip, limit=limit, search=search, status=status)

    def get_by_id(self, floor_id: int) -> Floor:
        floor = self._repo.get_by_id(floor_id)
        if not floor or not floor.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found.")
        return floor

    def create(self, data: FloorCreate, created_by: Optional[str] = None) -> Floor:
        if self._repo.floor_number_exists(data.floor_number):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Floor number {data.floor_number} already exists.",
            )
        floor = Floor(
            floor_number=data.floor_number,
            floor_name=data.floor_name,
            display_order=data.display_order,
            status=data.status,
            created_by=created_by,
        )
        return self._repo.create(floor)

    def update(self, floor_id: int, data: FloorUpdate, updated_by: Optional[str] = None) -> Floor:
        floor = self.get_by_id(floor_id)
        if data.floor_number is not None and data.floor_number != floor.floor_number:
            if self._repo.floor_number_exists(data.floor_number, exclude_id=floor_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Floor number {data.floor_number} already exists.",
                )
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(floor, field, value)
        floor.updated_by = updated_by
        return self._repo.save(floor)

    def delete(self, floor_id: int, deleted_by: Optional[str] = None) -> None:
        floor = self.get_by_id(floor_id)
        floor.soft_delete(deleted_by=deleted_by)
        self._repo.save(floor)


# ===========================================================================
# AmenityService
# ===========================================================================
class AmenityService:
    def __init__(self, db: Session) -> None:
        self._repo = AmenityRepository(db)

    def list(self, skip: int = 0, limit: int = 200, search: Optional[str] = None) -> tuple[list[Amenity], int]:
        return self._repo.list_active(skip=skip, limit=limit, search=search)

    def get_by_id(self, amenity_id: int) -> Amenity:
        a = self._repo.get_by_id(amenity_id)
        if not a or not a.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Amenity not found.")
        return a

    def create(self, data: AmenityCreate, created_by: Optional[str] = None) -> Amenity:
        if self._repo.name_exists(data.name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Amenity name already exists.")
        amenity = Amenity(**data.model_dump(), created_by=created_by)
        return self._repo.create(amenity)

    def update(self, amenity_id: int, data: AmenityUpdate, updated_by: Optional[str] = None) -> Amenity:
        amenity = self.get_by_id(amenity_id)
        if data.name is not None and data.name != amenity.name:
            if self._repo.name_exists(data.name, exclude_id=amenity_id):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Amenity name already exists.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(amenity, field, value)
        amenity.updated_by = updated_by
        return self._repo.save(amenity)

    def delete(self, amenity_id: int, deleted_by: Optional[str] = None) -> None:
        amenity = self.get_by_id(amenity_id)
        if amenity.is_system:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="System amenities cannot be deleted.",
            )
        amenity.soft_delete(deleted_by=deleted_by)
        self._repo.save(amenity)


# ===========================================================================
# BedTypeService
# ===========================================================================
class BedTypeService:
    def __init__(self, db: Session) -> None:
        self._repo = BedTypeRepository(db)

    def list(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> tuple[list[BedType], int]:
        return self._repo.list_active(skip=skip, limit=limit, search=search)

    def get_by_id(self, bed_type_id: int) -> BedType:
        bt = self._repo.get_by_id(bed_type_id)
        if not bt or not bt.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bed type not found.")
        return bt

    def create(self, data: BedTypeCreate, created_by: Optional[str] = None) -> BedType:
        if self._repo.name_exists(data.name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bed type name already exists.")
        bt = BedType(**data.model_dump(), created_by=created_by)
        return self._repo.create(bt)

    def update(self, bed_type_id: int, data: BedTypeUpdate, updated_by: Optional[str] = None) -> BedType:
        bt = self.get_by_id(bed_type_id)
        if data.name is not None and data.name != bt.name:
            if self._repo.name_exists(data.name, exclude_id=bed_type_id):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bed type name already exists.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(bt, field, value)
        bt.updated_by = updated_by
        return self._repo.save(bt)

    def delete(self, bed_type_id: int, deleted_by: Optional[str] = None) -> None:
        bt = self.get_by_id(bed_type_id)
        if bt.is_system:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="System bed types cannot be deleted.",
            )
        bt.soft_delete(deleted_by=deleted_by)
        self._repo.save(bt)


# ===========================================================================
# RoomTypeService
# ===========================================================================
class RoomTypeService:
    def __init__(self, db: Session) -> None:
        self._repo = RoomTypeRepository(db)
        self._amenity_repo = AmenityRepository(db)

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> tuple[list[RoomType], int]:
        return self._repo.list_active(skip=skip, limit=limit, search=search, status=status)

    def get_by_id(self, room_type_id: int) -> RoomType:
        rt = self._repo.get_by_id(room_type_id)
        if not rt or not rt.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room type not found.")
        return rt

    def create(self, data: RoomTypeCreate, created_by: Optional[str] = None) -> RoomType:
        if self._repo.name_exists(data.name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room type name already exists.")
        self._validate_pricing(data.base_price, data.weekend_price)

        amenities = self._amenity_repo.get_by_ids(data.amenity_ids)
        rt = RoomType(
            name=data.name,
            description=data.description,
            base_price=data.base_price,
            weekend_price=data.weekend_price,
            max_occupancy=data.max_occupancy,
            extra_bed_allowed=data.extra_bed_allowed,
            extra_bed_charge=data.extra_bed_charge,
            status=data.status,
            amenities=amenities,
            created_by=created_by,
        )
        self._repo.create(rt)
        if data.images:
            self._repo.replace_images(
                rt,
                [img.model_dump() for img in data.images],
            )
        return rt

    def update(self, room_type_id: int, data: RoomTypeUpdate, updated_by: Optional[str] = None) -> RoomType:
        rt = self.get_by_id(room_type_id)
        if data.name is not None and data.name != rt.name:
            if self._repo.name_exists(data.name, exclude_id=room_type_id):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room type name already exists.")
        base = data.base_price if data.base_price is not None else rt.base_price
        weekend = data.weekend_price if data.weekend_price is not None else rt.weekend_price
        self._validate_pricing(base, weekend)

        for field in ("name", "description", "base_price", "weekend_price",
                      "max_occupancy", "extra_bed_allowed", "extra_bed_charge", "status"):
            val = getattr(data, field, None)
            if val is not None:
                setattr(rt, field, val)

        if data.amenity_ids is not None:
            rt.amenities = self._amenity_repo.get_by_ids(data.amenity_ids)
        if data.images is not None:
            self._repo.replace_images(rt, [img.model_dump() for img in data.images])
        rt.updated_by = updated_by
        return self._repo.save(rt)

    def delete(self, room_type_id: int, deleted_by: Optional[str] = None) -> None:
        rt = self.get_by_id(room_type_id)
        rt.soft_delete(deleted_by=deleted_by)
        self._repo.save(rt)

    @staticmethod
    def _validate_pricing(base: Decimal, weekend: Optional[Decimal]) -> None:
        if base <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Base price must be greater than zero.",
            )
        if weekend is not None and weekend <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Weekend price must be greater than zero.",
            )


# ===========================================================================
# RoomService
# ===========================================================================
class RoomService:
    def __init__(self, db: Session) -> None:
        self._repo = RoomRepository(db)
        self._rt_repo = RoomTypeRepository(db)

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        floor_id: Optional[int] = None,
        room_type_id: Optional[int] = None,
        room_status: Optional[str] = None,
        housekeeping_status: Optional[str] = None,
        maintenance_status: Optional[str] = None,
        sort_by: str = "room_number",
        sort_dir: str = "asc",
    ) -> tuple[list[Room], int]:
        return self._repo.list_active(
            skip=skip, limit=limit, search=search,
            floor_id=floor_id, room_type_id=room_type_id,
            status=room_status,
            housekeeping_status=housekeeping_status,
            maintenance_status=maintenance_status,
            sort_by=sort_by, sort_dir=sort_dir,
        )

    def get_by_id(self, room_id: int) -> Room:
        room = self._repo.get_by_id(room_id)
        if not room or not room.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found.")
        return room

    def create(self, data: RoomCreate, created_by: Optional[str] = None) -> Room:
        self._assert_room_type_exists(data.room_type_id)
        if self._repo.room_number_exists(data.room_number):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Room number '{data.room_number}' already exists.",
            )
        room = Room(**data.model_dump(), created_by=created_by)
        return self._repo.create(room)

    def update(self, room_id: int, data: RoomUpdate, updated_by: Optional[str] = None) -> Room:
        room = self.get_by_id(room_id)
        if data.room_type_id is not None:
            self._assert_room_type_exists(data.room_type_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(room, field, value)
        room.updated_by = updated_by
        return self._repo.save(room)

    def delete(self, room_id: int, deleted_by: Optional[str] = None) -> None:
        room = self.get_by_id(room_id)
        room.soft_delete(deleted_by=deleted_by)
        self._repo.save(room)

    def bulk_create(self, data: RoomBulkCreate, created_by: Optional[str] = None) -> RoomBulkResult:
        created = 0
        failed = 0
        errors: list[dict[str, str]] = []
        for room_data in data.rooms:
            try:
                self.create(room_data, created_by=created_by)
                created += 1
            except HTTPException as exc:
                failed += 1
                errors.append({"room_number": room_data.room_number, "error": str(exc.detail)})
        return RoomBulkResult(created=created, failed=failed, errors=errors)

    def count_by_status(self) -> dict[str, int]:
        return self._repo.count_by_status()

    def _assert_room_type_exists(self, room_type_id: int) -> None:
        rt = self._rt_repo.get_by_id(room_type_id)
        if not rt or not rt.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room type {room_type_id} not found.",
            )


# ===========================================================================
# TaxService
# ===========================================================================
class TaxService:
    def __init__(self, db: Session) -> None:
        self._repo = TaxRepository(db)

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        applies_to: Optional[str] = None,
        tax_type: Optional[str] = None,
    ) -> tuple[list[Tax], int]:
        return self._repo.list_active(skip=skip, limit=limit, search=search,
                                      applies_to=applies_to, tax_type=tax_type)

    def get_by_id(self, tax_id: int) -> Tax:
        tax = self._repo.get_by_id(tax_id)
        if not tax or not tax.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tax not found.")
        return tax

    def create(self, data: TaxCreate, created_by: Optional[str] = None) -> Tax:
        if self._repo.code_exists(data.code):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Tax code '{data.code}' already exists.")
        self._validate_rate(data.tax_type, data.rate)
        tax = Tax(**data.model_dump(), created_by=created_by)
        return self._repo.create(tax)

    def update(self, tax_id: int, data: TaxUpdate, updated_by: Optional[str] = None) -> Tax:
        tax = self.get_by_id(tax_id)
        if data.rate is not None or data.tax_type is not None:
            t_type = data.tax_type or tax.tax_type
            rate = data.rate if data.rate is not None else tax.rate
            self._validate_rate(t_type, rate)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(tax, field, value)
        tax.updated_by = updated_by
        return self._repo.save(tax)

    def delete(self, tax_id: int, deleted_by: Optional[str] = None) -> None:
        tax = self.get_by_id(tax_id)
        tax.soft_delete(deleted_by=deleted_by)
        self._repo.save(tax)

    @staticmethod
    def _validate_rate(tax_type: str, rate: Decimal) -> None:
        if tax_type == "percentage" and rate > 100:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Percentage tax rate cannot exceed 100.",
            )
        if rate < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Tax rate cannot be negative.",
            )


# ===========================================================================
# PaymentMethodService
# ===========================================================================
class PaymentMethodService:
    def __init__(self, db: Session) -> None:
        self._repo = PaymentMethodRepository(db)

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        payment_type: Optional[str] = None,
    ) -> tuple[list[PaymentMethod], int]:
        return self._repo.list_active(skip=skip, limit=limit, search=search, payment_type=payment_type)

    def get_by_id(self, pm_id: int) -> PaymentMethod:
        pm = self._repo.get_by_id(pm_id)
        if not pm or not pm.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment method not found.")
        return pm

    def create(self, data: PaymentMethodCreate, created_by: Optional[str] = None) -> PaymentMethod:
        if self._repo.code_exists(data.code):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Payment method code '{data.code}' already exists.")
        pm = PaymentMethod(**data.model_dump(), created_by=created_by)
        return self._repo.create(pm)

    def update(self, pm_id: int, data: PaymentMethodUpdate, updated_by: Optional[str] = None) -> PaymentMethod:
        pm = self.get_by_id(pm_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(pm, field, value)
        pm.updated_by = updated_by
        return self._repo.save(pm)

    def delete(self, pm_id: int, deleted_by: Optional[str] = None) -> None:
        pm = self.get_by_id(pm_id)
        if pm.is_system:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="System payment methods cannot be deleted.")
        pm.soft_delete(deleted_by=deleted_by)
        self._repo.save(pm)


# ===========================================================================
# CurrencyService
# ===========================================================================
class CurrencyService:
    def __init__(self, db: Session) -> None:
        self._repo = CurrencyRepository(db)

    def list(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> tuple[list[Currency], int]:
        return self._repo.list_active(skip=skip, limit=limit, search=search)

    def get_by_id(self, currency_id: int) -> Currency:
        c = self._repo.get_by_id(currency_id)
        if not c or not c.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Currency not found.")
        return c

    def create(self, data: CurrencyCreate, created_by: Optional[str] = None) -> Currency:
        if self._repo.code_exists(data.code):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Currency '{data.code}' already exists.")
        if data.is_default:
            self._repo.clear_default()
        c = Currency(**data.model_dump(), created_by=created_by)
        return self._repo.create(c)

    def update(self, currency_id: int, data: CurrencyUpdate, updated_by: Optional[str] = None) -> Currency:
        c = self.get_by_id(currency_id)
        if data.is_default:
            self._repo.clear_default()
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(c, field, value)
        c.updated_by = updated_by
        return self._repo.save(c)

    def delete(self, currency_id: int, deleted_by: Optional[str] = None) -> None:
        c = self.get_by_id(currency_id)
        if c.is_default:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot delete the default currency.")
        c.soft_delete(deleted_by=deleted_by)
        self._repo.save(c)


# ===========================================================================
# SeasonService
# ===========================================================================
class SeasonService:
    def __init__(self, db: Session) -> None:
        self._repo = SeasonRepository(db)

    def list(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> tuple[list[Season], int]:
        return self._repo.list_active(skip=skip, limit=limit, search=search)

    def get_by_id(self, season_id: int) -> Season:
        s = self._repo.get_by_id(season_id)
        if not s or not s.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Season not found.")
        return s

    def create(self, data: SeasonCreate, created_by: Optional[str] = None) -> Season:
        overlapping = self._repo.find_overlapping(data.start_date, data.end_date)
        if overlapping:
            names = ", ".join(o.name for o in overlapping)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Date range overlaps with existing seasons: {names}",
            )
        s = Season(**data.model_dump(), created_by=created_by)
        return self._repo.create(s)

    def update(self, season_id: int, data: SeasonUpdate, updated_by: Optional[str] = None) -> Season:
        s = self.get_by_id(season_id)
        start = data.start_date or s.start_date
        end = data.end_date or s.end_date
        overlapping = self._repo.find_overlapping(start, end, exclude_id=season_id)
        if overlapping:
            names = ", ".join(o.name for o in overlapping)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Date range overlaps with existing seasons: {names}",
            )
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(s, field, value)
        s.updated_by = updated_by
        return self._repo.save(s)

    def delete(self, season_id: int, deleted_by: Optional[str] = None) -> None:
        s = self.get_by_id(season_id)
        s.soft_delete(deleted_by=deleted_by)
        self._repo.save(s)


# ===========================================================================
# RatePlanService
# ===========================================================================
class RatePlanService:
    def __init__(self, db: Session) -> None:
        self._repo = RatePlanRepository(db)

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        meal_plan: Optional[str] = None,
    ) -> tuple[list[RatePlan], int]:
        return self._repo.list_active(skip=skip, limit=limit, search=search, meal_plan=meal_plan)

    def get_by_id(self, rate_plan_id: int) -> RatePlan:
        rp = self._repo.get_by_id(rate_plan_id)
        if not rp or not rp.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rate plan not found.")
        return rp

    def create(self, data: RatePlanCreate, created_by: Optional[str] = None) -> RatePlan:
        if self._repo.code_exists(data.code):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Rate plan code '{data.code}' already exists.")
        self._validate_stay(data.min_stay_nights, data.max_stay_nights)
        for rate in data.season_rates:
            if rate.price_per_night <= 0:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="All season rates must have price_per_night > 0.",
                )
        if data.is_default:
            self._repo.clear_default()
        rp = RatePlan(
            name=data.name,
            code=data.code,
            description=data.description,
            meal_plan=data.meal_plan,
            is_default=data.is_default,
            min_stay_nights=data.min_stay_nights,
            max_stay_nights=data.max_stay_nights,
            cancellation_policy=data.cancellation_policy,
            created_by=created_by,
        )
        self._repo.create(rp)
        if data.season_rates:
            self._repo.replace_season_rates(
                rp.id,
                [r.model_dump() for r in data.season_rates],
            )
        return self._repo.get_by_id(rp.id)  # type: ignore[return-value]

    def update(self, rate_plan_id: int, data: RatePlanUpdate, updated_by: Optional[str] = None) -> RatePlan:
        rp = self.get_by_id(rate_plan_id)
        min_s = data.min_stay_nights or rp.min_stay_nights
        max_s = data.max_stay_nights if data.max_stay_nights is not None else rp.max_stay_nights
        self._validate_stay(min_s, max_s)
        if data.is_default:
            self._repo.clear_default()
        for field in ("name", "description", "meal_plan", "is_default",
                      "min_stay_nights", "max_stay_nights", "cancellation_policy", "is_active"):
            val = getattr(data, field, None)
            if val is not None:
                setattr(rp, field, val)
        if data.season_rates is not None:
            self._repo.replace_season_rates(rp.id, [r.model_dump() for r in data.season_rates])
        rp.updated_by = updated_by
        return self._repo.save(rp)

    def delete(self, rate_plan_id: int, deleted_by: Optional[str] = None) -> None:
        rp = self.get_by_id(rate_plan_id)
        rp.soft_delete(deleted_by=deleted_by)
        self._repo.save(rp)

    @staticmethod
    def _validate_stay(min_s: int, max_s: Optional[int]) -> None:
        if max_s is not None and max_s < min_s:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="max_stay_nights must be >= min_stay_nights.",
            )
