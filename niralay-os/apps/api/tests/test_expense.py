"""
Integration tests for Expense API.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


class TestExpenseCategories:
    def test_create_category(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/expenses/categories",
            json={"name": "Staff Salaries", "display_order": 1},
        )
        assert r.status_code == 201
        body = r.json()
        assert body["data"]["name"] == "Staff Salaries"

    def test_duplicate_name_rejected(self, superuser_client: TestClient) -> None:
        superuser_client.post("/api/v1/expenses/categories", json={"name": "DupExpCat"})
        r = superuser_client.post("/api/v1/expenses/categories", json={"name": "DupExpCat"})
        assert r.status_code == 409

    def test_list_categories(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/expenses/categories")
        assert r.status_code == 200
        body = r.json()
        assert "data" in body
        assert isinstance(body["data"], list)

    def test_update_category(self, superuser_client: TestClient) -> None:
        create = superuser_client.post("/api/v1/expenses/categories", json={"name": "UpdateExpCat"})
        cat_id = create.json()["data"]["id"]
        r = superuser_client.patch(
            f"/api/v1/expenses/categories/{cat_id}",
            json={"name": "UpdateExpCatRenamed"},
        )
        assert r.status_code == 200
        assert r.json()["data"]["name"] == "UpdateExpCatRenamed"

    def test_delete_category(self, superuser_client: TestClient) -> None:
        create = superuser_client.post("/api/v1/expenses/categories", json={"name": "DeleteExpCat"})
        cat_id = create.json()["data"]["id"]
        r = superuser_client.delete(f"/api/v1/expenses/categories/{cat_id}")
        assert r.status_code == 200


class TestExpenses:
    def test_create_expense(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/expenses",
            json={
                "description": "Staff Salary July 2025",
                "amount": 50000.00,
                "tax_amount": 0,
                "total_amount": 50000.00,
                "expense_date": "2025-07-15",
                "payment_method": "bank_transfer",
                "vendor_name": "Payroll",
            },
        )
        assert r.status_code == 201
        body = r.json()
        assert body["data"]["description"] == "Staff Salary July 2025"
        assert float(body["data"]["total_amount"]) == 50000.00

    def test_create_expense_with_category(self, superuser_client: TestClient) -> None:
        # Create a category first
        cat = superuser_client.post(
            "/api/v1/expenses/categories",
            json={"name": "Utilities"},
        )
        cat_id = cat.json()["data"]["id"]

        r = superuser_client.post(
            "/api/v1/expenses",
            json={
                "description": "Electricity bill",
                "amount": 15000.00,
                "tax_amount": 2700.00,
                "total_amount": 17700.00,
                "expense_date": "2025-07-14",
                "category_id": cat_id,
                "payment_method": "upi",
            },
        )
        assert r.status_code == 201
        body = r.json()
        assert body["data"]["category_id"] == cat_id

    def test_create_expense_missing_description_rejected(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/expenses",
            json={
                "amount": 1000,
                "expense_date": "2025-07-01",
            },
        )
        assert r.status_code == 422

    def test_create_expense_future_date_allowed(self, superuser_client: TestClient) -> None:
        """Pre-approved future expenses should be allowed."""
        r = superuser_client.post(
            "/api/v1/expenses",
            json={
                "description": "Advance booking fee",
                "amount": 5000.00,
                "total_amount": 5000.00,
                "expense_date": "2030-01-01",
                "payment_method": "cash",
            },
        )
        assert r.status_code == 201

    def test_list_expenses(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/expenses")
        assert r.status_code == 200
        body = r.json()
        assert "items" in body
        assert "total" in body

    def test_list_expenses_with_search(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/expenses?search=Salary")
        assert r.status_code == 200

    def test_list_expenses_date_range(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/expenses?date_from=2025-07-01&date_to=2025-07-31")
        assert r.status_code == 200

    def test_get_expense(self, superuser_client: TestClient) -> None:
        create = superuser_client.post(
            "/api/v1/expenses",
            json={
                "description": "Get Test Expense",
                "amount": 100.00,
                "total_amount": 100.00,
                "expense_date": "2025-07-01",
            },
        )
        exp_id = create.json()["data"]["id"]
        r = superuser_client.get(f"/api/v1/expenses/{exp_id}")
        assert r.status_code == 200
        assert r.json()["data"]["id"] == exp_id

    def test_update_expense(self, superuser_client: TestClient) -> None:
        create = superuser_client.post(
            "/api/v1/expenses",
            json={
                "description": "Update Test Expense",
                "amount": 200.00,
                "total_amount": 200.00,
                "expense_date": "2025-07-01",
            },
        )
        exp_id = create.json()["data"]["id"]
        r = superuser_client.patch(
            f"/api/v1/expenses/{exp_id}",
            json={"vendor_name": "Updated Vendor", "notes": "Updated"},
        )
        assert r.status_code == 200
        assert r.json()["data"]["vendor_name"] == "Updated Vendor"

    def test_delete_expense(self, superuser_client: TestClient) -> None:
        create = superuser_client.post(
            "/api/v1/expenses",
            json={
                "description": "Delete Test Expense",
                "amount": 50.00,
                "total_amount": 50.00,
                "expense_date": "2025-07-01",
            },
        )
        exp_id = create.json()["data"]["id"]
        r = superuser_client.delete(f"/api/v1/expenses/{exp_id}")
        assert r.status_code == 200

    def test_get_nonexistent_expense(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/expenses/99999")
        assert r.status_code == 404

    def test_expense_summary(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/expenses/summary")
        assert r.status_code == 200
