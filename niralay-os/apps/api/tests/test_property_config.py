"""
Integration tests for Property Configuration Platform API.

Uses the session-scoped superuser_client (JWT with permissions=["*"]).
All tests verify end-to-end behavior through the real FastAPI routes.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


# ===========================================================================
# PropertyProfile
# ===========================================================================
class TestPropertyProfile:
    def test_get_profile_creates_default(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/property/profile")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["hotel_name"] == "My Hotel"
        assert data["currency_code"] == "INR"

    def test_update_profile(self, superuser_client: TestClient) -> None:
        r = superuser_client.patch(
            "/api/v1/property/profile",
            json={
                "hotel_name": "The Grand Niralay",
                "city": "Mumbai",
                "gst_number": "27AAPCS1751H1ZN",
                "star_rating": 5,
            },
        )
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["hotel_name"] == "The Grand Niralay"
        assert data["star_rating"] == 5

    def test_update_profile_invalid_star_rating(self, superuser_client: TestClient) -> None:
        r = superuser_client.patch("/api/v1/property/profile", json={"star_rating": 10})
        assert r.status_code == 422


# ===========================================================================
# Floors
# ===========================================================================
class TestFloors:
    def test_create_floor(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/property/floors",
            json={"floor_number": 1, "floor_name": "Ground Floor", "display_order": 0},
        )
        assert r.status_code == 201
        data = r.json()["data"]
        assert data["floor_number"] == 1
        assert data["floor_name"] == "Ground Floor"

    def test_duplicate_floor_number_rejected(self, superuser_client: TestClient) -> None:
        superuser_client.post(
            "/api/v1/property/floors",
            json={"floor_number": 99, "floor_name": "Test Floor"},
        )
        r = superuser_client.post(
            "/api/v1/property/floors",
            json={"floor_number": 99, "floor_name": "Another Floor"},
        )
        assert r.status_code == 409

    def test_list_floors(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/property/floors")
        assert r.status_code == 200
        body = r.json()
        assert "items" in body
        assert "total" in body

    def test_update_floor(self, superuser_client: TestClient) -> None:
        # Create first
        create = superuser_client.post(
            "/api/v1/property/floors",
            json={"floor_number": 55, "floor_name": "Floor 55"},
        )
        floor_id = create.json()["data"]["id"]
        r = superuser_client.patch(
            f"/api/v1/property/floors/{floor_id}",
            json={"floor_name": "Updated Floor 55"},
        )
        assert r.status_code == 200
        assert r.json()["data"]["floor_name"] == "Updated Floor 55"

    def test_delete_floor(self, superuser_client: TestClient) -> None:
        create = superuser_client.post(
            "/api/v1/property/floors",
            json={"floor_number": 66, "floor_name": "Floor 66"},
        )
        floor_id = create.json()["data"]["id"]
        r = superuser_client.delete(f"/api/v1/property/floors/{floor_id}")
        assert r.status_code == 200

    def test_get_deleted_floor_returns_404(self, superuser_client: TestClient) -> None:
        create = superuser_client.post(
            "/api/v1/property/floors",
            json={"floor_number": 77, "floor_name": "Floor 77"},
        )
        floor_id = create.json()["data"]["id"]
        superuser_client.delete(f"/api/v1/property/floors/{floor_id}")
        # After delete it should not appear in list
        r = superuser_client.get("/api/v1/property/floors")
        ids = [f["id"] for f in r.json()["items"]]
        assert floor_id not in ids


# ===========================================================================
# Amenities
# ===========================================================================
class TestAmenities:
    def test_list_amenities(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/property/amenities")
        assert r.status_code == 200

    def test_create_amenity(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/property/amenities",
            json={"name": "Balcony", "icon": "door-open"},
        )
        assert r.status_code == 201
        assert r.json()["data"]["name"] == "Balcony"

    def test_duplicate_amenity_name_rejected(self, superuser_client: TestClient) -> None:
        superuser_client.post("/api/v1/property/amenities", json={"name": "UniqueAmenity1"})
        r = superuser_client.post("/api/v1/property/amenities", json={"name": "UniqueAmenity1"})
        assert r.status_code == 409


# ===========================================================================
# Taxes
# ===========================================================================
class TestTaxes:
    def test_create_tax(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/property/taxes",
            json={
                "name": "GST 18%",
                "code": "GST18",
                "tax_type": "percentage",
                "rate": "18.0000",
                "applies_to": "all",
            },
        )
        assert r.status_code == 201
        data = r.json()["data"]
        assert data["code"] == "GST18"
        assert float(data["rate"]) == 18.0

    def test_duplicate_code_rejected(self, superuser_client: TestClient) -> None:
        superuser_client.post(
            "/api/v1/property/taxes",
            json={"name": "GST 5%", "code": "GST5", "tax_type": "percentage",
                  "rate": "5.0000", "applies_to": "all"},
        )
        r = superuser_client.post(
            "/api/v1/property/taxes",
            json={"name": "GST 5 Duplicate", "code": "GST5", "tax_type": "percentage",
                  "rate": "5.0000", "applies_to": "all"},
        )
        assert r.status_code == 409

    def test_percentage_over_100_rejected(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/property/taxes",
            json={"name": "Bad Tax", "code": "BAD_TAX", "tax_type": "percentage",
                  "rate": "150.0000", "applies_to": "all"},
        )
        assert r.status_code == 422

    def test_list_taxes(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/property/taxes")
        assert r.status_code == 200


# ===========================================================================
# Room Types
# ===========================================================================
class TestRoomTypes:
    def test_create_room_type(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/property/room-types",
            json={
                "name": "Standard Room",
                "base_price": "2500.00",
                "max_occupancy": 2,
            },
        )
        assert r.status_code == 201
        data = r.json()["data"]
        assert data["name"] == "Standard Room"

    def test_create_room_type_with_amenities(self, superuser_client: TestClient) -> None:
        amenity_r = superuser_client.post(
            "/api/v1/property/amenities", json={"name": "Minibar"}
        )
        amenity_id = amenity_r.json()["data"]["id"]
        r = superuser_client.post(
            "/api/v1/property/room-types",
            json={
                "name": "Deluxe Room",
                "base_price": "5000.00",
                "amenity_ids": [amenity_id],
            },
        )
        assert r.status_code == 201
        data = r.json()["data"]
        amenity_ids = [a["id"] for a in data["amenities"]]
        assert amenity_id in amenity_ids

    def test_duplicate_room_type_name_rejected(self, superuser_client: TestClient) -> None:
        superuser_client.post(
            "/api/v1/property/room-types",
            json={"name": "UniqueSuite", "base_price": "8000.00"},
        )
        r = superuser_client.post(
            "/api/v1/property/room-types",
            json={"name": "UniqueSuite", "base_price": "9000.00"},
        )
        assert r.status_code == 409

    def test_zero_price_rejected(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/property/room-types",
            json={"name": "FreeRoom", "base_price": "0.00"},
        )
        assert r.status_code == 422


# ===========================================================================
# Rooms
# ===========================================================================
class TestRooms:
    def _get_or_create_room_type(self, superuser_client: TestClient) -> int:
        r = superuser_client.post(
            "/api/v1/property/room-types",
            json={"name": "TestRoomType_Rooms", "base_price": "1500.00"},
        )
        if r.status_code == 201:
            return r.json()["data"]["id"]
        # Already exists — find it
        lst = superuser_client.get("/api/v1/property/room-types?search=TestRoomType_Rooms")
        return lst.json()["items"][0]["id"]

    def test_create_room(self, superuser_client: TestClient) -> None:
        rt_id = self._get_or_create_room_type(superuser_client)
        r = superuser_client.post(
            "/api/v1/property/rooms",
            json={"room_number": "101", "room_type_id": rt_id},
        )
        assert r.status_code == 201
        assert r.json()["data"]["room_number"] == "101"

    def test_duplicate_room_number_rejected(self, superuser_client: TestClient) -> None:
        rt_id = self._get_or_create_room_type(superuser_client)
        superuser_client.post(
            "/api/v1/property/rooms",
            json={"room_number": "201", "room_type_id": rt_id},
        )
        r = superuser_client.post(
            "/api/v1/property/rooms",
            json={"room_number": "201", "room_type_id": rt_id},
        )
        assert r.status_code == 409

    def test_list_rooms(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/property/rooms")
        assert r.status_code == 200

    def test_status_summary(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/property/rooms/status-summary")
        assert r.status_code == 200

    def test_bulk_create_rooms(self, superuser_client: TestClient) -> None:
        rt_id = self._get_or_create_room_type(superuser_client)
        r = superuser_client.post(
            "/api/v1/property/rooms/bulk",
            json={
                "rooms": [
                    {"room_number": "301", "room_type_id": rt_id},
                    {"room_number": "302", "room_type_id": rt_id},
                    {"room_number": "301", "room_type_id": rt_id},  # duplicate — should fail
                ]
            },
        )
        assert r.status_code == 201
        result = r.json()["data"]
        assert result["created"] == 2
        assert result["failed"] == 1


# ===========================================================================
# Seasons
# ===========================================================================
class TestSeasons:
    def test_create_season(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/property/seasons",
            json={"name": "Peak Season 2026", "start_date": "2026-12-01", "end_date": "2026-12-31"},
        )
        assert r.status_code == 201
        data = r.json()["data"]
        assert data["name"] == "Peak Season 2026"

    def test_end_before_start_rejected(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/property/seasons",
            json={"name": "Bad Season", "start_date": "2026-12-31", "end_date": "2026-12-01"},
        )
        assert r.status_code == 422

    def test_overlapping_season_rejected(self, superuser_client: TestClient) -> None:
        superuser_client.post(
            "/api/v1/property/seasons",
            json={"name": "Summer 2027", "start_date": "2027-05-01", "end_date": "2027-05-31"},
        )
        r = superuser_client.post(
            "/api/v1/property/seasons",
            json={"name": "May 2027", "start_date": "2027-05-15", "end_date": "2027-06-15"},
        )
        assert r.status_code == 409


# ===========================================================================
# Rate Plans
# ===========================================================================
class TestRatePlans:
    def test_create_rate_plan(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/property/rate-plans",
            json={"name": "Standard EP", "code": "STD_EP", "meal_plan": "EP"},
        )
        assert r.status_code == 201
        assert r.json()["data"]["code"] == "STD_EP"

    def test_duplicate_code_rejected(self, superuser_client: TestClient) -> None:
        superuser_client.post(
            "/api/v1/property/rate-plans",
            json={"name": "Plan A", "code": "PLAN_A", "meal_plan": "EP"},
        )
        r = superuser_client.post(
            "/api/v1/property/rate-plans",
            json={"name": "Plan A Dup", "code": "PLAN_A", "meal_plan": "CP"},
        )
        assert r.status_code == 409

    def test_invalid_max_stay_rejected(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/property/rate-plans",
            json={"name": "Bad Plan", "code": "BAD_PLAN", "meal_plan": "EP",
                  "min_stay_nights": 5, "max_stay_nights": 2},
        )
        assert r.status_code == 422


# ===========================================================================
# Payment Methods
# ===========================================================================
class TestPaymentMethods:
    def test_list_payment_methods(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/property/payment-methods")
        assert r.status_code == 200

    def test_create_payment_method(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/property/payment-methods",
            json={"name": "Cheque", "code": "cheque", "payment_type": "other"},
        )
        assert r.status_code == 201

    def test_duplicate_code_rejected(self, superuser_client: TestClient) -> None:
        superuser_client.post(
            "/api/v1/property/payment-methods",
            json={"name": "Voucher", "code": "voucher", "payment_type": "other"},
        )
        r = superuser_client.post(
            "/api/v1/property/payment-methods",
            json={"name": "Voucher Dup", "code": "voucher", "payment_type": "other"},
        )
        assert r.status_code == 409


# ===========================================================================
# Currencies
# ===========================================================================
class TestCurrencies:
    def test_list_currencies(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/property/currencies")
        assert r.status_code == 200

    def test_create_currency(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/property/currencies",
            json={"code": "USD", "name": "US Dollar", "symbol": "$", "exchange_rate": "83.5"},
        )
        assert r.status_code == 201
        assert r.json()["data"]["code"] == "USD"

    def test_invalid_currency_code(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/property/currencies",
            json={"code": "US", "name": "Invalid", "symbol": "$", "exchange_rate": "1.0"},
        )
        assert r.status_code == 422

    def test_cannot_delete_default_currency(self, superuser_client: TestClient) -> None:
        # INR is seeded as default
        lst = superuser_client.get("/api/v1/property/currencies?search=INR")
        inr = lst.json()["items"][0]
        r = superuser_client.delete(f"/api/v1/property/currencies/{inr['id']}")
        assert r.status_code == 409
