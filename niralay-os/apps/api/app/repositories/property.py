"""
Property configuration repositories for NiralayOS.

Pure database I/O — no business logic.
Every repository extends BaseRepository[ModelT].
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.property import (
    Amenity,
    BedType,
    Currency,
    Floor,
    PaymentMethod,
    PropertyProfile,
    RatePlan,
    RatePlanSeasonRate,
    RoomType,
    RoomTypeImage,
    Room,
    Season,
    Tax,
)
from app.repositories.base import BaseRepository


# ---------------------------------------------------------------------------
# PropertyProfile  (singleton)
# ---------------------------------------------------------------------------
class PropertyProfileRepository(BaseRepository[PropertyProfile]):
    def __init__(self, db: Session) -> None:
        super().__init__(PropertyProfile, db)

    def get_singleton(self) -> Optional[PropertyProfile]:
        """Return the single property profile row, or None if not yet created."""
        return self.db.query(PropertyProfile).filter(
            PropertyProfile.is_active.is_(True)
        ).first()

    def get_or_create(self) -> PropertyProfile:
        """Return existing profile or create a default one."""
        profile = self.get_singleton()
        if profile is None:
            profile = PropertyProfile(hotel_name="My Hotel")
            self.db.add(profile)
            self.db.flush()
            self.db.refresh(profile)
        return profile


# ---------------------------------------------------------------------------
# Floor
# ---------------------------------------------------------------------------
class FloorRepository(BaseRepository[Floor]):
    def __init__(self, db: Session) -> None:
        super().__init__(Floor, db)

    def list_active(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> tuple[list[Floor], int]:
        q = self.db.query(Floor).filter(Floor.is_active.is_(True))
        if search:
            term = f"%{search}%"
            q = q.filter(
                or_(
                    Floor.floor_name.ilike(term),
                    Floor.floor_number.cast(type_=None).ilike(term),
                )
            )
        if status:
            q = q.filter(Floor.status == status)
        total = q.count()
        items = q.order_by(Floor.display_order, Floor.floor_number).offset(skip).limit(limit).all()
        return items, total

    def floor_number_exists(self, floor_number: int, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(Floor.id).filter(
            Floor.floor_number == floor_number,
            Floor.is_active.is_(True),
        )
        if exclude_id:
            q = q.filter(Floor.id != exclude_id)
        return q.first() is not None


# ---------------------------------------------------------------------------
# Amenity
# ---------------------------------------------------------------------------
class AmenityRepository(BaseRepository[Amenity]):
    def __init__(self, db: Session) -> None:
        super().__init__(Amenity, db)

    def list_active(
        self,
        skip: int = 0,
        limit: int = 200,
        search: Optional[str] = None,
    ) -> tuple[list[Amenity], int]:
        q = self.db.query(Amenity).filter(Amenity.is_active.is_(True))
        if search:
            q = q.filter(Amenity.name.ilike(f"%{search}%"))
        total = q.count()
        items = q.order_by(Amenity.name).offset(skip).limit(limit).all()
        return items, total

    def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(Amenity.id).filter(Amenity.name == name)
        if exclude_id:
            q = q.filter(Amenity.id != exclude_id)
        return q.first() is not None

    def get_by_ids(self, ids: list[int]) -> list[Amenity]:
        if not ids:
            return []
        return self.db.query(Amenity).filter(Amenity.id.in_(ids)).all()


# ---------------------------------------------------------------------------
# BedType
# ---------------------------------------------------------------------------
class BedTypeRepository(BaseRepository[BedType]):
    def __init__(self, db: Session) -> None:
        super().__init__(BedType, db)

    def list_active(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> tuple[list[BedType], int]:
        q = self.db.query(BedType).filter(BedType.is_active.is_(True))
        if search:
            q = q.filter(BedType.name.ilike(f"%{search}%"))
        total = q.count()
        items = q.order_by(BedType.name).offset(skip).limit(limit).all()
        return items, total

    def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(BedType.id).filter(BedType.name == name)
        if exclude_id:
            q = q.filter(BedType.id != exclude_id)
        return q.first() is not None


# ---------------------------------------------------------------------------
# RoomType
# ---------------------------------------------------------------------------
class RoomTypeRepository(BaseRepository[RoomType]):
    def __init__(self, db: Session) -> None:
        super().__init__(RoomType, db)

    def list_active(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> tuple[list[RoomType], int]:
        q = self.db.query(RoomType).filter(RoomType.is_active.is_(True))
        if search:
            q = q.filter(RoomType.name.ilike(f"%{search}%"))
        if status:
            q = q.filter(RoomType.status == status)
        total = q.count()
        items = q.order_by(RoomType.name).offset(skip).limit(limit).all()
        return items, total

    def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(RoomType.id).filter(RoomType.name == name)
        if exclude_id:
            q = q.filter(RoomType.id != exclude_id)
        return q.first() is not None

    def replace_images(self, room_type: RoomType, images_data: list[dict]) -> None:
        """Replace all images for a room type."""
        self.db.query(RoomTypeImage).filter(
            RoomTypeImage.room_type_id == room_type.id
        ).delete(synchronize_session=False)
        for img in images_data:
            self.db.add(RoomTypeImage(room_type_id=room_type.id, **img))
        self.db.flush()


# ---------------------------------------------------------------------------
# Room
# ---------------------------------------------------------------------------
class RoomRepository(BaseRepository[Room]):
    def __init__(self, db: Session) -> None:
        super().__init__(Room, db)

    def list_active(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        floor_id: Optional[int] = None,
        room_type_id: Optional[int] = None,
        status: Optional[str] = None,
        housekeeping_status: Optional[str] = None,
        maintenance_status: Optional[str] = None,
        sort_by: str = "room_number",
        sort_dir: str = "asc",
    ) -> tuple[list[Room], int]:
        q = self.db.query(Room).filter(Room.is_active.is_(True))
        if search:
            q = q.filter(Room.room_number.ilike(f"%{search}%"))
        if floor_id is not None:
            q = q.filter(Room.floor_id == floor_id)
        if room_type_id is not None:
            q = q.filter(Room.room_type_id == room_type_id)
        if status:
            q = q.filter(Room.status == status)
        if housekeeping_status:
            q = q.filter(Room.housekeeping_status == housekeeping_status)
        if maintenance_status:
            q = q.filter(Room.maintenance_status == maintenance_status)
        total = q.count()
        sort_col = getattr(Room, sort_by, Room.room_number)
        if sort_dir == "desc":
            sort_col = sort_col.desc()
        items = q.order_by(sort_col).offset(skip).limit(limit).all()
        return items, total

    def room_number_exists(self, room_number: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(Room.id).filter(
            Room.room_number == room_number,
            Room.is_active.is_(True),
        )
        if exclude_id:
            q = q.filter(Room.id != exclude_id)
        return q.first() is not None

    def count_by_status(self) -> dict[str, int]:
        """Return a dict of {status: count} for active rooms."""
        rows = (
            self.db.query(Room.status, Room.id)
            .filter(Room.is_active.is_(True))
            .all()
        )
        result: dict[str, int] = {}
        for row in rows:
            result[row.status] = result.get(row.status, 0) + 1
        return result


# ---------------------------------------------------------------------------
# Tax
# ---------------------------------------------------------------------------
class TaxRepository(BaseRepository[Tax]):
    def __init__(self, db: Session) -> None:
        super().__init__(Tax, db)

    def list_active(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        applies_to: Optional[str] = None,
        tax_type: Optional[str] = None,
    ) -> tuple[list[Tax], int]:
        q = self.db.query(Tax).filter(Tax.is_active.is_(True))
        if search:
            term = f"%{search}%"
            q = q.filter(or_(Tax.name.ilike(term), Tax.code.ilike(term)))
        if applies_to:
            q = q.filter(Tax.applies_to == applies_to)
        if tax_type:
            q = q.filter(Tax.tax_type == tax_type)
        total = q.count()
        items = q.order_by(Tax.name).offset(skip).limit(limit).all()
        return items, total

    def code_exists(self, code: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(Tax.id).filter(Tax.code == code)
        if exclude_id:
            q = q.filter(Tax.id != exclude_id)
        return q.first() is not None

    def get_by_code(self, code: str) -> Optional[Tax]:
        return self.db.query(Tax).filter(Tax.code == code).first()


# ---------------------------------------------------------------------------
# PaymentMethod
# ---------------------------------------------------------------------------
class PaymentMethodRepository(BaseRepository[PaymentMethod]):
    def __init__(self, db: Session) -> None:
        super().__init__(PaymentMethod, db)

    def list_active(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        payment_type: Optional[str] = None,
    ) -> tuple[list[PaymentMethod], int]:
        q = self.db.query(PaymentMethod).filter(PaymentMethod.is_active.is_(True))
        if search:
            q = q.filter(PaymentMethod.name.ilike(f"%{search}%"))
        if payment_type:
            q = q.filter(PaymentMethod.payment_type == payment_type)
        total = q.count()
        items = q.order_by(PaymentMethod.name).offset(skip).limit(limit).all()
        return items, total

    def code_exists(self, code: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(PaymentMethod.id).filter(PaymentMethod.code == code)
        if exclude_id:
            q = q.filter(PaymentMethod.id != exclude_id)
        return q.first() is not None


# ---------------------------------------------------------------------------
# Currency
# ---------------------------------------------------------------------------
class CurrencyRepository(BaseRepository[Currency]):
    def __init__(self, db: Session) -> None:
        super().__init__(Currency, db)

    def list_active(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> tuple[list[Currency], int]:
        q = self.db.query(Currency).filter(Currency.is_active.is_(True))
        if search:
            term = f"%{search}%"
            q = q.filter(or_(Currency.name.ilike(term), Currency.code.ilike(term)))
        total = q.count()
        items = q.order_by(Currency.code).offset(skip).limit(limit).all()
        return items, total

    def code_exists(self, code: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(Currency.id).filter(Currency.code == code)
        if exclude_id:
            q = q.filter(Currency.id != exclude_id)
        return q.first() is not None

    def get_default(self) -> Optional[Currency]:
        return self.db.query(Currency).filter(
            Currency.is_default.is_(True), Currency.is_active.is_(True)
        ).first()

    def clear_default(self) -> None:
        self.db.query(Currency).filter(Currency.is_default.is_(True)).update(
            {"is_default": False}, synchronize_session=False
        )
        self.db.flush()


# ---------------------------------------------------------------------------
# Season
# ---------------------------------------------------------------------------
class SeasonRepository(BaseRepository[Season]):
    def __init__(self, db: Session) -> None:
        super().__init__(Season, db)

    def list_active(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> tuple[list[Season], int]:
        q = self.db.query(Season).filter(Season.is_active.is_(True))
        if search:
            q = q.filter(Season.name.ilike(f"%{search}%"))
        total = q.count()
        items = q.order_by(Season.start_date).offset(skip).limit(limit).all()
        return items, total

    def find_overlapping(
        self,
        start: date,
        end: date,
        exclude_id: Optional[int] = None,
    ) -> list[Season]:
        """Return seasons whose date range overlaps with [start, end]."""
        q = self.db.query(Season).filter(
            Season.is_active.is_(True),
            Season.start_date <= end,
            Season.end_date >= start,
        )
        if exclude_id:
            q = q.filter(Season.id != exclude_id)
        return q.all()


# ---------------------------------------------------------------------------
# RatePlan
# ---------------------------------------------------------------------------
class RatePlanRepository(BaseRepository[RatePlan]):
    def __init__(self, db: Session) -> None:
        super().__init__(RatePlan, db)

    def list_active(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        meal_plan: Optional[str] = None,
    ) -> tuple[list[RatePlan], int]:
        q = self.db.query(RatePlan).filter(RatePlan.is_active.is_(True))
        if search:
            term = f"%{search}%"
            q = q.filter(or_(RatePlan.name.ilike(term), RatePlan.code.ilike(term)))
        if meal_plan:
            q = q.filter(RatePlan.meal_plan == meal_plan)
        total = q.count()
        items = q.order_by(RatePlan.name).offset(skip).limit(limit).all()
        return items, total

    def code_exists(self, code: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(RatePlan.id).filter(RatePlan.code == code)
        if exclude_id:
            q = q.filter(RatePlan.id != exclude_id)
        return q.first() is not None

    def clear_default(self) -> None:
        self.db.query(RatePlan).filter(RatePlan.is_default.is_(True)).update(
            {"is_default": False}, synchronize_session=False
        )
        self.db.flush()

    def replace_season_rates(
        self, rate_plan_id: int, rates_data: list[dict]
    ) -> None:
        self.db.query(RatePlanSeasonRate).filter(
            RatePlanSeasonRate.rate_plan_id == rate_plan_id
        ).delete(synchronize_session=False)
        for r in rates_data:
            self.db.add(RatePlanSeasonRate(rate_plan_id=rate_plan_id, **r))
        self.db.flush()
