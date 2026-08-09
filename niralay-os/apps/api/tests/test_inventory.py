"""
Integration tests for Inventory API.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


class TestInventoryCategories:
    def test_create_category(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/inventory/categories",
            json={"name": "F&B Ingredients", "display_order": 1, "color": "#155E4B"},
        )
        assert r.status_code == 201
        body = r.json()
        assert body["data"]["name"] == "F&B Ingredients"
        assert body["data"]["color"] == "#155E4B"

    def test_duplicate_name_rejected(self, superuser_client: TestClient) -> None:
        superuser_client.post("/api/v1/inventory/categories", json={"name": "DuplicateCat"})
        r = superuser_client.post("/api/v1/inventory/categories", json={"name": "DuplicateCat"})
        assert r.status_code == 409

    def test_invalid_color_rejected(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/inventory/categories",
            json={"name": "BadColor", "color": "not-a-color"},
        )
        assert r.status_code == 422

    def test_list_categories(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/inventory/categories")
        assert r.status_code == 200
        body = r.json()
        assert "data" in body
        assert isinstance(body["data"], list)

    def test_update_category(self, superuser_client: TestClient) -> None:
        create = superuser_client.post(
            "/api/v1/inventory/categories",
            json={"name": "UpdateMe", "display_order": 0},
        )
        cat_id = create.json()["data"]["id"]
        r = superuser_client.patch(
            f"/api/v1/inventory/categories/{cat_id}",
            json={"name": "Updated", "display_order": 5},
        )
        assert r.status_code == 200
        assert r.json()["data"]["name"] == "Updated"

    def test_delete_category(self, superuser_client: TestClient) -> None:
        create = superuser_client.post(
            "/api/v1/inventory/categories",
            json={"name": "DeleteMe"},
        )
        cat_id = create.json()["data"]["id"]
        r = superuser_client.delete(f"/api/v1/inventory/categories/{cat_id}")
        assert r.status_code == 200

    def test_get_nonexistent_category(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/inventory/categories/99999")
        assert r.status_code == 404


class TestStoreLocations:
    def test_create_location(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/inventory/locations",
            json={"name": "Main Store", "code": "MAIN-01"},
        )
        assert r.status_code == 201
        body = r.json()
        assert body["data"]["code"] == "MAIN-01"

    def test_duplicate_code_rejected(self, superuser_client: TestClient) -> None:
        superuser_client.post("/api/v1/inventory/locations", json={"name": "Store X", "code": "DUP-01"})
        r = superuser_client.post("/api/v1/inventory/locations", json={"name": "Store Y", "code": "DUP-01"})
        assert r.status_code == 409

    def test_list_locations(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/inventory/locations")
        assert r.status_code == 200


class TestInventoryItems:
    def test_create_item_with_zero_stock(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/inventory/items",
            json={
                "sku": "TEST-ITEM-001",
                "name": "Test Basmati Rice",
                "unit": "kg",
                "item_type": "consumable",
                "current_stock": 0,
                "minimum_stock": 10,
            },
        )
        assert r.status_code == 201
        body = r.json()
        assert body["data"]["sku"] == "TEST-ITEM-001"
        assert float(body["data"]["current_stock"]) == 0

    def test_create_item_with_opening_stock(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/inventory/items",
            json={
                "sku": "RICE-OPENING-002",
                "name": "Basmati Rice Premium",
                "unit": "kg",
                "item_type": "consumable",
                "current_stock": 50,
                "minimum_stock": 10,
                "purchase_price": 85.0,
            },
        )
        assert r.status_code == 201
        body = r.json()
        # Stock should be set via opening movement
        assert float(body["data"]["current_stock"]) == 50.0

    def test_duplicate_sku_rejected(self, superuser_client: TestClient) -> None:
        superuser_client.post(
            "/api/v1/inventory/items",
            json={"sku": "DUP-SKU-999", "name": "Item A", "unit": "piece"},
        )
        r = superuser_client.post(
            "/api/v1/inventory/items",
            json={"sku": "DUP-SKU-999", "name": "Item B", "unit": "piece"},
        )
        assert r.status_code == 409

    def test_invalid_item_type_rejected(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/inventory/items",
            json={"sku": "INVALID-TYPE", "name": "Bad Type", "unit": "piece", "item_type": "invalid"},
        )
        assert r.status_code == 422

    def test_list_items(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/inventory/items")
        assert r.status_code == 200
        body = r.json()
        assert "items" in body
        assert "total" in body

    def test_list_items_with_search(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/inventory/items?search=Rice")
        assert r.status_code == 200

    def test_list_items_with_stock_level_filter(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/inventory/items?stock_level=critical")
        assert r.status_code == 200

    def test_get_item(self, superuser_client: TestClient) -> None:
        create = superuser_client.post(
            "/api/v1/inventory/items",
            json={"sku": "GET-TEST-001", "name": "Get Test Item", "unit": "piece"},
        )
        item_id = create.json()["data"]["id"]
        r = superuser_client.get(f"/api/v1/inventory/items/{item_id}")
        assert r.status_code == 200
        assert r.json()["data"]["id"] == item_id

    def test_update_item(self, superuser_client: TestClient) -> None:
        create = superuser_client.post(
            "/api/v1/inventory/items",
            json={"sku": "UPDATE-TEST-001", "name": "Update Test", "unit": "kg"},
        )
        item_id = create.json()["data"]["id"]
        r = superuser_client.patch(
            f"/api/v1/inventory/items/{item_id}",
            json={"minimum_stock": 5.0, "supplier_name": "Test Supplier"},
        )
        assert r.status_code == 200
        assert r.json()["data"]["supplier_name"] == "Test Supplier"

    def test_delete_item(self, superuser_client: TestClient) -> None:
        create = superuser_client.post(
            "/api/v1/inventory/items",
            json={"sku": "DELETE-TEST-001", "name": "Delete Test", "unit": "piece"},
        )
        item_id = create.json()["data"]["id"]
        r = superuser_client.delete(f"/api/v1/inventory/items/{item_id}")
        assert r.status_code == 200

    def test_get_nonexistent_item(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/inventory/items/99999")
        assert r.status_code == 404

    def test_get_low_stock_alerts(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/inventory/items/alerts")
        assert r.status_code == 200


class TestStockMovements:
    def _create_item(self, superuser_client: TestClient, sku: str, stock: float = 100) -> int:
        r = superuser_client.post(
            "/api/v1/inventory/items",
            json={
                "sku": sku,
                "name": f"Test Item {sku}",
                "unit": "kg",
                "item_type": "consumable",
                "current_stock": stock,
                "minimum_stock": 10,
            },
        )
        assert r.status_code == 201
        return r.json()["data"]["id"]

    def test_purchase_movement_increases_stock(self, superuser_client: TestClient) -> None:
        item_id = self._create_item(superuser_client, "MOV-PURCHASE-001", stock=0)
        r = superuser_client.post(
            f"/api/v1/inventory/items/{item_id}/movements",
            json={"movement_type": "purchase", "quantity": 50, "unit_cost": 85.0},
        )
        assert r.status_code == 201
        body = r.json()["data"]
        assert float(body["stock_after"]) == 50.0
        assert float(body["stock_before"]) == 0.0

    def test_consumption_movement_decreases_stock(self, superuser_client: TestClient) -> None:
        item_id = self._create_item(superuser_client, "MOV-CONSUME-001", stock=50)
        r = superuser_client.post(
            f"/api/v1/inventory/items/{item_id}/movements",
            json={"movement_type": "consumption", "quantity": 10},
        )
        assert r.status_code == 201
        body = r.json()["data"]
        assert float(body["stock_after"]) == 40.0

    def test_insufficient_stock_rejected(self, superuser_client: TestClient) -> None:
        item_id = self._create_item(superuser_client, "MOV-INSUF-001", stock=5)
        r = superuser_client.post(
            f"/api/v1/inventory/items/{item_id}/movements",
            json={"movement_type": "consumption", "quantity": 100},
        )
        assert r.status_code == 422

    def test_invalid_movement_type_rejected(self, superuser_client: TestClient) -> None:
        item_id = self._create_item(superuser_client, "MOV-BADTYPE-001", stock=10)
        r = superuser_client.post(
            f"/api/v1/inventory/items/{item_id}/movements",
            json={"movement_type": "fly_away", "quantity": 5},
        )
        assert r.status_code == 422

    def test_list_movements(self, superuser_client: TestClient) -> None:
        item_id = self._create_item(superuser_client, "MOV-LIST-001", stock=20)
        r = superuser_client.get(f"/api/v1/inventory/items/{item_id}/movements")
        assert r.status_code == 200
        body = r.json()
        assert "items" in body
        # Should have at least the opening movement
        assert body["total"] >= 1
