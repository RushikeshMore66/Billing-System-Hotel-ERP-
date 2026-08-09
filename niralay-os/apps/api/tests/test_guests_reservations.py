"""
Integration tests for Guests and Reservations API.

Covers:
- Guest CRUD
- Reservation creation with server-side numbering
- Double-booking prevention
- Date validation
- Status transitions
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _today() -> str:
    return date.today().isoformat()

def _offset(n: int) -> str:
    return (date.today() + timedelta(days=n)).isoformat()


def _create_guest(client: TestClient, suffix: str = "") -> dict:
    r = client.post(
        "/api/v1/guests",
        json={
            "full_name": f"Test Guest{suffix}",
            "email": f"testguest{suffix}@niralayos.test",
            "phone": "9876543210",
        },
    )
    assert r.status_code == 201, r.text
    return r.json()["data"]


def _get_room_type_id(client: TestClient) -> int | None:
    """Retrieve the first available room type for reservation creation."""
    r = client.get("/api/v1/property/room-types?size=1")
    if r.status_code != 200:
        return None
    items = r.json().get("items", [])
    return items[0]["id"] if items else None


def _get_room_id(client: TestClient) -> int | None:
    """Retrieve the first available room for reservation creation."""
    r = client.get("/api/v1/property/rooms?size=1")
    if r.status_code != 200:
        return None
    items = r.json().get("items", [])
    return items[0]["id"] if items else None


def _make_reservation(
    client: TestClient,
    guest_id: int,
    room_type_id: int,
    check_in: str,
    check_out: str,
    room_id: int | None = None,
) -> dict:
    payload = {
        "guest_id": guest_id,
        "room_type_id": room_type_id,
        "check_in_date": check_in,
        "check_out_date": check_out,
        "adults": 2,
    }
    if room_id:
        payload["room_id"] = room_id
    r = client.post("/api/v1/reservations", json=payload)
    assert r.status_code == 201, r.text
    return r.json()["data"]


# ─── Guest Tests ──────────────────────────────────────────────────────────────

class TestGuests:
    def test_create_guest(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/guests",
            json={
                "full_name": "Arjun Mehta",
                "email": "arjun.mehta@example.com",
                "phone": "9123456789",
                "nationality": "Indian",
            },
        )
        assert r.status_code == 201
        body = r.json()["data"]
        assert body["full_name"] == "Arjun Mehta"
        assert body["email"] == "arjun.mehta@example.com"
        assert "id" in body
        assert "uuid" in body

    def test_guest_full_name_required(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/guests",
            json={"email": "nofullname@example.com"},
        )
        assert r.status_code == 422

    def test_list_guests(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/guests")
        assert r.status_code == 200
        body = r.json()
        assert "items" in body
        assert "total" in body

    def test_list_guests_search(self, superuser_client: TestClient) -> None:
        superuser_client.post(
            "/api/v1/guests",
            json={"full_name": "Priya Search Test", "email": "priya.search@test.com"},
        )
        r = superuser_client.get("/api/v1/guests?search=Priya+Search")
        assert r.status_code == 200
        body = r.json()
        assert body["total"] >= 1

    def test_get_guest(self, superuser_client: TestClient) -> None:
        guest = _create_guest(superuser_client, "_get_test")
        r = superuser_client.get(f"/api/v1/guests/{guest['id']}")
        assert r.status_code == 200
        assert r.json()["data"]["id"] == guest["id"]

    def test_get_nonexistent_guest(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/guests/99999")
        assert r.status_code == 404

    def test_update_guest(self, superuser_client: TestClient) -> None:
        guest = _create_guest(superuser_client, "_update_test")
        r = superuser_client.patch(
            f"/api/v1/guests/{guest['id']}",
            json={"notes": "VIP guest", "nationality": "Indian"},
        )
        assert r.status_code == 200
        assert r.json()["data"]["notes"] == "VIP guest"

    def test_delete_guest(self, superuser_client: TestClient) -> None:
        guest = _create_guest(superuser_client, "_delete_test")
        r = superuser_client.delete(f"/api/v1/guests/{guest['id']}")
        assert r.status_code == 200


# ─── Reservation Tests ────────────────────────────────────────────────────────

class TestReservations:
    def test_list_reservations(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/reservations")
        assert r.status_code == 200
        body = r.json()
        assert "items" in body
        assert "total" in body

    def test_list_reservations_filter_by_status(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/reservations?status=pending")
        assert r.status_code == 200

    def test_create_reservation_requires_room_type(
        self, superuser_client: TestClient
    ) -> None:
        guest = _create_guest(superuser_client, "_no_room_type")
        r = superuser_client.post(
            "/api/v1/reservations",
            json={
                "guest_id": guest["id"],
                "check_in_date": _offset(1),
                "check_out_date": _offset(3),
            },
        )
        assert r.status_code == 422

    def test_checkout_must_be_after_checkin(
        self, superuser_client: TestClient
    ) -> None:
        room_type_id = _get_room_type_id(superuser_client)
        if room_type_id is None:
            pytest.skip("No room types configured")
        guest = _create_guest(superuser_client, "_bad_dates")
        r = superuser_client.post(
            "/api/v1/reservations",
            json={
                "guest_id": guest["id"],
                "room_type_id": room_type_id,
                "check_in_date": _offset(5),
                "check_out_date": _offset(3),  # Before check-in!
            },
        )
        assert r.status_code == 400

    def test_same_day_checkout_rejected(
        self, superuser_client: TestClient
    ) -> None:
        room_type_id = _get_room_type_id(superuser_client)
        if room_type_id is None:
            pytest.skip("No room types configured")
        guest = _create_guest(superuser_client, "_same_day")
        r = superuser_client.post(
            "/api/v1/reservations",
            json={
                "guest_id": guest["id"],
                "room_type_id": room_type_id,
                "check_in_date": _offset(1),
                "check_out_date": _offset(1),  # Same day!
            },
        )
        assert r.status_code == 400

    def test_reservation_has_sequential_number(
        self, superuser_client: TestClient
    ) -> None:
        room_type_id = _get_room_type_id(superuser_client)
        if room_type_id is None:
            pytest.skip("No room types configured")
        guest = _create_guest(superuser_client, "_seq_num")
        res = _make_reservation(
            superuser_client, guest["id"], room_type_id,
            _offset(10), _offset(12),
        )
        assert res["reservation_number"]
        assert len(res["reservation_number"]) > 4

    def test_reservation_nights_calculated_server_side(
        self, superuser_client: TestClient
    ) -> None:
        room_type_id = _get_room_type_id(superuser_client)
        if room_type_id is None:
            pytest.skip("No room types configured")
        guest = _create_guest(superuser_client, "_nights_calc")
        res = _make_reservation(
            superuser_client, guest["id"], room_type_id,
            _offset(20), _offset(23),  # 3 nights
        )
        assert res["nights"] == 3

    def test_update_reservation_status(
        self, superuser_client: TestClient
    ) -> None:
        room_type_id = _get_room_type_id(superuser_client)
        if room_type_id is None:
            pytest.skip("No room types configured")
        guest = _create_guest(superuser_client, "_status_update")
        res = _make_reservation(
            superuser_client, guest["id"], room_type_id,
            _offset(30), _offset(32),
        )
        r = superuser_client.patch(
            f"/api/v1/reservations/{res['id']}",
            json={"status": "confirmed"},
        )
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "confirmed"

    def test_get_nonexistent_reservation(
        self, superuser_client: TestClient
    ) -> None:
        r = superuser_client.get("/api/v1/reservations/99999")
        assert r.status_code == 404


class TestDoubleBookingPrevention:
    """Double-booking prevention: same room cannot be reserved for overlapping dates."""

    def test_double_booking_same_dates_rejected(
        self, superuser_client: TestClient
    ) -> None:
        room_type_id = _get_room_type_id(superuser_client)
        room_id = _get_room_id(superuser_client)
        if room_type_id is None or room_id is None:
            pytest.skip("No rooms/room types configured")

        guest_a = _create_guest(superuser_client, "_dbl_a")
        guest_b = _create_guest(superuser_client, "_dbl_b")

        check_in = _offset(50)
        check_out = _offset(53)

        # First reservation succeeds
        _make_reservation(
            superuser_client, guest_a["id"], room_type_id,
            check_in, check_out, room_id=room_id,
        )

        # Exact same dates → should conflict
        r = superuser_client.post(
            "/api/v1/reservations",
            json={
                "guest_id": guest_b["id"],
                "room_type_id": room_type_id,
                "room_id": room_id,
                "check_in_date": check_in,
                "check_out_date": check_out,
            },
        )
        assert r.status_code == 409

    def test_double_booking_overlapping_dates_rejected(
        self, superuser_client: TestClient
    ) -> None:
        room_type_id = _get_room_type_id(superuser_client)
        room_id = _get_room_id(superuser_client)
        if room_type_id is None or room_id is None:
            pytest.skip("No rooms/room types configured")

        guest_a = _create_guest(superuser_client, "_ovrlp_a")
        guest_b = _create_guest(superuser_client, "_ovrlp_b")

        # Book room for days 60-65
        _make_reservation(
            superuser_client, guest_a["id"], room_type_id,
            _offset(60), _offset(65), room_id=room_id,
        )

        # Try booking overlapping: days 63-68 (overlaps 63-65)
        r = superuser_client.post(
            "/api/v1/reservations",
            json={
                "guest_id": guest_b["id"],
                "room_type_id": room_type_id,
                "room_id": room_id,
                "check_in_date": _offset(63),
                "check_out_date": _offset(68),
            },
        )
        assert r.status_code == 409

    def test_adjacent_dates_allowed(
        self, superuser_client: TestClient
    ) -> None:
        """Check-out day is not an overlap — next guest can check in same day."""
        room_type_id = _get_room_type_id(superuser_client)
        room_id = _get_room_id(superuser_client)
        if room_type_id is None or room_id is None:
            pytest.skip("No rooms/room types configured")

        guest_a = _create_guest(superuser_client, "_adj_a")
        guest_b = _create_guest(superuser_client, "_adj_b")

        # Guest A: days 70-73
        _make_reservation(
            superuser_client, guest_a["id"], room_type_id,
            _offset(70), _offset(73), room_id=room_id,
        )

        # Guest B: days 73-75 — starts exactly when A checks out → OK
        r = superuser_client.post(
            "/api/v1/reservations",
            json={
                "guest_id": guest_b["id"],
                "room_type_id": room_type_id,
                "room_id": room_id,
                "check_in_date": _offset(73),
                "check_out_date": _offset(75),
            },
        )
        assert r.status_code == 201

    def test_cancelled_reservation_does_not_block(
        self, superuser_client: TestClient
    ) -> None:
        """A cancelled reservation should free the room."""
        room_type_id = _get_room_type_id(superuser_client)
        room_id = _get_room_id(superuser_client)
        if room_type_id is None or room_id is None:
            pytest.skip("No rooms/room types configured")

        guest_a = _create_guest(superuser_client, "_cancel_a")
        guest_b = _create_guest(superuser_client, "_cancel_b")

        check_in = _offset(80)
        check_out = _offset(83)

        res = _make_reservation(
            superuser_client, guest_a["id"], room_type_id,
            check_in, check_out, room_id=room_id,
        )

        # Cancel the first reservation
        superuser_client.patch(
            f"/api/v1/reservations/{res['id']}",
            json={"status": "cancelled"},
        )

        # Now guest B should be able to book the same room/dates
        r = superuser_client.post(
            "/api/v1/reservations",
            json={
                "guest_id": guest_b["id"],
                "room_type_id": room_type_id,
                "room_id": room_id,
                "check_in_date": check_in,
                "check_out_date": check_out,
            },
        )
        assert r.status_code == 201
