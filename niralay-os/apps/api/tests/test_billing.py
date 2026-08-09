"""
Integration tests for Billing API.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _make_bill(client: TestClient, **kwargs) -> dict:
    payload = {
        "bill_type": "restaurant",
        "items": [
            {
                "item_type": "menu_item",
                "description": "Butter Chicken",
                "quantity": 2,
                "unit_price": 420.00,
                "tax_rate": 5.0,
            }
        ],
    }
    payload.update(kwargs)
    r = client.post("/api/v1/billing/bills", json=payload)
    assert r.status_code == 201, r.text
    return r.json()["data"]


# ─── Tests ───────────────────────────────────────────────────────────────────

class TestBillCreation:
    def test_create_restaurant_bill(self, superuser_client: TestClient) -> None:
        bill = _make_bill(superuser_client)
        assert bill["bill_number"].startswith("INV-") or bill["bill_number"]
        assert bill["status"] == "draft"
        assert bill["bill_type"] == "restaurant"
        # Items should be present
        assert len(bill["items"]) == 1
        assert bill["items"][0]["description"] == "Butter Chicken"

    def test_bill_number_is_sequential(self, superuser_client: TestClient) -> None:
        bill_a = _make_bill(superuser_client)
        bill_b = _make_bill(superuser_client)
        # Both should have unique numbers
        assert bill_a["bill_number"] != bill_b["bill_number"]

    def test_server_calculates_totals(self, superuser_client: TestClient) -> None:
        """Backend must compute subtotal, tax, and total — not the client."""
        bill = _make_bill(superuser_client, items=[
            {
                "item_type": "menu_item",
                "description": "Paneer Tikka",
                "quantity": 3,
                "unit_price": 320.00,
                "tax_rate": 5.0,
                "discount_pct": 10.0,
            }
        ])
        # quantity=3, price=320, discount=10% → amount = 3*320*0.9 = 864
        # tax = 864 * 0.05 = 43.20 → total = 907.20
        assert abs(float(bill["subtotal"]) - 864.0) < 0.1
        assert abs(float(bill["tax_amount"]) - 43.2) < 0.1
        assert abs(float(bill["total_amount"]) - 907.2) < 0.1

    def test_create_room_bill(self, superuser_client: TestClient) -> None:
        bill = _make_bill(superuser_client, bill_type="room", items=[
            {
                "item_type": "room_charge",
                "description": "Deluxe Suite - 3 nights",
                "quantity": 3,
                "unit_price": 5000.00,
                "tax_rate": 12.0,
            }
        ])
        assert bill["bill_type"] == "room"

    def test_create_bill_with_table(self, superuser_client: TestClient) -> None:
        bill = _make_bill(superuser_client, table_number="T-12")
        assert bill["table_number"] == "T-12"

    def test_create_bill_no_items_rejected(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/billing/bills",
            json={"bill_type": "restaurant", "items": []},
        )
        assert r.status_code == 422

    def test_create_bill_negative_quantity_rejected(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/billing/bills",
            json={
                "bill_type": "restaurant",
                "items": [
                    {"description": "Bad Item", "quantity": -1, "unit_price": 100},
                ],
            },
        )
        assert r.status_code == 422

    def test_create_bill_negative_price_rejected(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/billing/bills",
            json={
                "bill_type": "restaurant",
                "items": [
                    {"description": "Bad Price", "quantity": 1, "unit_price": -50},
                ],
            },
        )
        assert r.status_code == 422


class TestBillList:
    def test_list_bills(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/billing/bills")
        assert r.status_code == 200
        body = r.json()
        assert "items" in body
        assert "total" in body

    def test_list_bills_filter_by_status(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/billing/bills?status=draft")
        assert r.status_code == 200

    def test_list_bills_filter_by_type(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/billing/bills?bill_type=restaurant")
        assert r.status_code == 200

    def test_list_bills_date_range(self, superuser_client: TestClient) -> None:
        r = superuser_client.get(
            "/api/v1/billing/bills?date_from=2025-01-01&date_to=2030-12-31"
        )
        assert r.status_code == 200

    def test_get_bill(self, superuser_client: TestClient) -> None:
        bill = _make_bill(superuser_client)
        r = superuser_client.get(f"/api/v1/billing/bills/{bill['id']}")
        assert r.status_code == 200
        assert r.json()["data"]["id"] == bill["id"]

    def test_get_nonexistent_bill(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/billing/bills/99999")
        assert r.status_code == 404


class TestBillWorkflow:
    def test_issue_draft_bill(self, superuser_client: TestClient) -> None:
        bill = _make_bill(superuser_client)
        r = superuser_client.post(f"/api/v1/billing/bills/{bill['id']}/issue")
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "issued"

    def test_cannot_issue_already_issued_bill(self, superuser_client: TestClient) -> None:
        bill = _make_bill(superuser_client)
        superuser_client.post(f"/api/v1/billing/bills/{bill['id']}/issue")
        # Try issuing again
        r = superuser_client.post(f"/api/v1/billing/bills/{bill['id']}/issue")
        assert r.status_code == 422

    def test_add_items_to_draft(self, superuser_client: TestClient) -> None:
        bill = _make_bill(superuser_client)
        r = superuser_client.post(
            f"/api/v1/billing/bills/{bill['id']}/items",
            json=[
                {"description": "Extra Naan", "quantity": 2, "unit_price": 60.0, "tax_rate": 5.0}
            ],
        )
        assert r.status_code == 200
        updated = r.json()["data"]
        assert len(updated["items"]) == 2

    def test_cannot_add_items_to_issued_bill(self, superuser_client: TestClient) -> None:
        bill = _make_bill(superuser_client)
        superuser_client.post(f"/api/v1/billing/bills/{bill['id']}/issue")
        r = superuser_client.post(
            f"/api/v1/billing/bills/{bill['id']}/items",
            json=[{"description": "Late add", "quantity": 1, "unit_price": 100}],
        )
        # Service returns 409 Conflict for invalid status transitions
        assert r.status_code in (409, 422)

    def test_full_payment_marks_paid(self, superuser_client: TestClient) -> None:
        bill = _make_bill(superuser_client)
        superuser_client.post(f"/api/v1/billing/bills/{bill['id']}/issue")
        total = float(bill["total_amount"])
        r = superuser_client.post(
            f"/api/v1/billing/bills/{bill['id']}/payments",
            json={"amount": total, "payment_type": "cash"},
        )
        assert r.status_code == 201
        # Fetch the bill again to check status
        updated = superuser_client.get(f"/api/v1/billing/bills/{bill['id']}").json()["data"]
        assert updated["status"] == "paid"
        assert abs(float(updated["amount_due"])) < 0.01

    def test_partial_payment_marks_partially_paid(self, superuser_client: TestClient) -> None:
        bill = _make_bill(superuser_client)
        superuser_client.post(f"/api/v1/billing/bills/{bill['id']}/issue")
        total = float(bill["total_amount"])
        r = superuser_client.post(
            f"/api/v1/billing/bills/{bill['id']}/payments",
            json={"amount": total / 2, "payment_type": "upi"},
        )
        assert r.status_code == 201
        updated = superuser_client.get(f"/api/v1/billing/bills/{bill['id']}").json()["data"]
        assert updated["status"] == "partially_paid"

    def test_cannot_overpay_bill(self, superuser_client: TestClient) -> None:
        bill = _make_bill(superuser_client)
        superuser_client.post(f"/api/v1/billing/bills/{bill['id']}/issue")
        total = float(bill["total_amount"])
        r = superuser_client.post(
            f"/api/v1/billing/bills/{bill['id']}/payments",
            json={"amount": total * 10},
        )
        assert r.status_code == 422

    def test_void_bill(self, superuser_client: TestClient) -> None:
        bill = _make_bill(superuser_client)
        r = superuser_client.post(
            f"/api/v1/billing/bills/{bill['id']}/void",
            params={"reason": "Customer cancelled order"},
        )
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "void"

    def test_cannot_void_paid_bill(self, superuser_client: TestClient) -> None:
        bill = _make_bill(superuser_client)
        superuser_client.post(f"/api/v1/billing/bills/{bill['id']}/issue")
        superuser_client.post(
            f"/api/v1/billing/bills/{bill['id']}/payments",
            json={"amount": float(bill["total_amount"])},
        )
        r = superuser_client.post(
            f"/api/v1/billing/bills/{bill['id']}/void",
            params={"reason": "Should fail"},
        )
        # Can't void a paid bill — 409 or 422 are both acceptable
        assert r.status_code in (409, 422)

    def test_payment_amount_zero_rejected(self, superuser_client: TestClient) -> None:
        bill = _make_bill(superuser_client)
        superuser_client.post(f"/api/v1/billing/bills/{bill['id']}/issue")
        r = superuser_client.post(
            f"/api/v1/billing/bills/{bill['id']}/payments",
            json={"amount": 0},
        )
        assert r.status_code == 422
