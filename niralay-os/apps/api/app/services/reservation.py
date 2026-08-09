"""
Reservation Service — with double-booking prevention.
"""
from typing import Optional, Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, func
from fastapi import HTTPException, status
from app.models.reservation import Reservation, ReservationStatusHistory
from app.models.property import Room
from app.repositories.reservation import ReservationRepository
from app.schemas.reservation import ReservationCreate, ReservationUpdate
from app.core.constants import ReservationStatus
from datetime import datetime, timezone


def _generate_reservation_number(db: Session) -> str:
    """Generate sequential reservation number from BusinessSettings format."""
    from app.models.settings import BusinessSettings

    settings = db.scalars(select(BusinessSettings)).first()
    now = datetime.now(timezone.utc)

    if settings:
        seq = settings.reservation_sequence_start
        settings.reservation_sequence_start += 1
        db.flush()
        fmt = settings.reservation_number_format
        res_num = (
            fmt
            .replace("{YYYY}", str(now.year))
            .replace("{MM}", f"{now.month:02d}")
            .replace("{DD}", f"{now.day:02d}")
            .replace("{SEQ}", f"{seq:05d}")
        )
    else:
        # Fallback
        res_num = f"RES-{now.year}-{now.month:02d}-{now.microsecond}"

    return res_num


class ReservationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ReservationRepository(db)

    def get_reservation(self, reservation_id: int) -> Reservation:
        reservation = self.repo.get_by_id(reservation_id)
        if not reservation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
        return reservation

    def get_reservation_by_number(self, reservation_number: str) -> Reservation:
        reservation = self.repo.get_by_number(reservation_number)
        if not reservation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
        return reservation

    def search_reservations(
        self,
        query: Optional[str] = None,
        status_filter: Optional[ReservationStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[Reservation], int]:
        return self.repo.search(query=query, status=status_filter, skip=skip, limit=limit)

    def check_room_availability(
        self,
        room_id: int,
        check_in: object,
        check_out: object,
        exclude_reservation_id: Optional[int] = None,
    ) -> bool:
        """
        Return True if the room is available for the given date range.

        A conflict exists when another reservation for the same room overlaps:
            existing.check_in < requested.check_out
            AND existing.check_out > requested.check_in
        (Standard interval overlap test)
        """
        stmt = select(Reservation).where(
            Reservation.room_id == room_id,
            Reservation.status.notin_([
                ReservationStatus.CANCELLED,
                ReservationStatus.NO_SHOW,
                ReservationStatus.CHECKED_OUT,
            ]),
            Reservation.check_in_date < check_out,
            Reservation.check_out_date > check_in,
        )
        if exclude_reservation_id:
            stmt = stmt.where(Reservation.id != exclude_reservation_id)

        conflict = self.db.scalars(stmt).first()
        return conflict is None

    def create_reservation(self, data: ReservationCreate, current_user_name: str = "System") -> Reservation:
        # Date validation
        if data.check_out_date <= data.check_in_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Check-out date must be after check-in date",
            )

        # Double-booking prevention
        if data.room_id is not None:
            if not self.check_room_availability(data.room_id, data.check_in_date, data.check_out_date):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"Room {data.room_id} is already reserved for the requested dates "
                        f"({data.check_in_date} – {data.check_out_date})"
                    ),
                )

        reservation = Reservation(**data.model_dump())
        reservation.reservation_number = _generate_reservation_number(self.db)
        reservation.nights = (reservation.check_out_date - reservation.check_in_date).days

        reservation = self.repo.create(reservation)

        history = ReservationStatusHistory(
            reservation_id=reservation.id,
            to_status=reservation.status,
            changed_by=current_user_name,
            changed_at=datetime.now(timezone.utc),
        )
        self.repo.add_status_history(history)

        return reservation

    def update_reservation(
        self,
        reservation_id: int,
        data: ReservationUpdate,
        current_user_name: str = "System",
    ) -> Reservation:
        reservation = self.get_reservation(reservation_id)
        update_data = data.model_dump(exclude_unset=True)

        old_status = reservation.status

        # Apply new check-in/check-out dates and re-validate
        new_check_in = update_data.get("check_in_date", reservation.check_in_date)
        new_check_out = update_data.get("check_out_date", reservation.check_out_date)
        new_room_id = update_data.get("room_id", reservation.room_id)

        if new_check_out <= new_check_in:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Check-out date must be after check-in date",
            )

        # Re-check availability if room or dates changed
        if new_room_id is not None and (
            new_room_id != reservation.room_id
            or new_check_in != reservation.check_in_date
            or new_check_out != reservation.check_out_date
        ):
            if not self.check_room_availability(
                new_room_id, new_check_in, new_check_out, exclude_reservation_id=reservation_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"Room {new_room_id} is already reserved for the requested dates "
                        f"({new_check_in} – {new_check_out})"
                    ),
                )

        for key, value in update_data.items():
            setattr(reservation, key, value)

        # Recompute nights if dates changed
        if "check_in_date" in update_data or "check_out_date" in update_data:
            reservation.nights = (reservation.check_out_date - reservation.check_in_date).days

        reservation = self.repo.save(reservation)

        if "status" in update_data and old_status != update_data["status"]:
            history = ReservationStatusHistory(
                reservation_id=reservation.id,
                from_status=old_status,
                to_status=reservation.status,
                changed_by=current_user_name,
                changed_at=datetime.now(timezone.utc),
            )
            self.repo.add_status_history(history)

        return reservation
