"""
Integration tests for Restaurant Configuration API.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


class TestRestaurantCategories:
    def test_create_category(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/restaurant/categories",
            json={"name": "Main Course", "display_order": 1},
        )
        assert r.status_code == 201
        assert r.json()["data"]["name"] == "Main Course"

    def test_duplicate_name_rejected(self, superuser_client: TestClient) -> None:
        superuser_client.post("/api/v1/restaurant/categories", json={"name": "Beverages"})
        r = superuser_client.post("/api/v1/restaurant/categories", json={"name": "Beverages"})
        assert r.status_code == 409

    def test_invalid_color_rejected(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/restaurant/categories",
            json={"name": "Desserts", "color": "not-a-color"},
        )
        assert r.status_code == 422

    def test_list_categories(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/restaurant/categories")
        assert r.status_code == 200


class TestMenuCategories:
    def test_create_menu_category(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/restaurant/menu-categories",
            json={"name": "Indian Starters"},
        )
        assert r.status_code == 201

    def test_self_parent_rejected(self, superuser_client: TestClient) -> None:
        create = superuser_client.post(
            "/api/v1/restaurant/menu-categories",
            json={"name": "SelfRefCat"},
        )
        cat_id = create.json()["data"]["id"]
        r = superuser_client.patch(
            f"/api/v1/restaurant/menu-categories/{cat_id}",
            json={"parent_id": cat_id},
        )
        assert r.status_code == 422


class TestKitchenStations:
    def test_create_station(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/restaurant/kitchen-stations",
            json={"name": "Main Kitchen", "display_order": 1},
        )
        assert r.status_code == 201

    def test_duplicate_name_rejected(self, superuser_client: TestClient) -> None:
        superuser_client.post("/api/v1/restaurant/kitchen-stations", json={"name": "Grill Station"})
        r = superuser_client.post("/api/v1/restaurant/kitchen-stations", json={"name": "Grill Station"})
        assert r.status_code == 409


class TestMenuItems:
    def test_create_menu_item(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/restaurant/menu-items",
            json={
                "item_code": "BRG001",
                "name": "Classic Burger",
                "price": "250.00",
                "food_type": "non_veg",
            },
        )
        assert r.status_code == 201
        data = r.json()["data"]
        assert data["item_code"] == "BRG001"
        assert data["food_type"] == "non_veg"

    def test_duplicate_item_code_rejected(self, superuser_client: TestClient) -> None:
        superuser_client.post(
            "/api/v1/restaurant/menu-items",
            json={"item_code": "VGN001", "name": "Veg Burger", "price": "200.00"},
        )
        r = superuser_client.post(
            "/api/v1/restaurant/menu-items",
            json={"item_code": "VGN001", "name": "Another Veg Burger", "price": "210.00"},
        )
        assert r.status_code == 409

    def test_invalid_food_type_rejected(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/restaurant/menu-items",
            json={"item_code": "BAD001", "name": "Bad Food", "price": "100.00", "food_type": "meat"},
        )
        assert r.status_code == 422

    def test_list_menu_items(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/restaurant/menu-items")
        assert r.status_code == 200

    def test_filter_by_food_type(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/restaurant/menu-items?food_type=veg")
        assert r.status_code == 200

    def test_delete_menu_item(self, superuser_client: TestClient) -> None:
        create = superuser_client.post(
            "/api/v1/restaurant/menu-items",
            json={"item_code": "DEL001", "name": "To Delete", "price": "50.00"},
        )
        item_id = create.json()["data"]["id"]
        r = superuser_client.delete(f"/api/v1/restaurant/menu-items/{item_id}")
        assert r.status_code == 200


class TestMenuModifiers:
    def test_create_modifier(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/restaurant/modifiers",
            json={
                "name": "Spice Level",
                "modifier_type": "single",
                "is_required": True,
                "options": [
                    {"name": "Mild", "price_impact": "0.00"},
                    {"name": "Medium", "price_impact": "0.00"},
                    {"name": "Hot", "price_impact": "0.00"},
                ],
            },
        )
        assert r.status_code == 201
        data = r.json()["data"]
        assert data["name"] == "Spice Level"
        assert len(data["options"]) == 3

    def test_invalid_selection_range_rejected(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/restaurant/modifiers",
            json={
                "name": "Invalid Modifier",
                "modifier_type": "multi",
                "min_selections": 5,
                "max_selections": 2,
            },
        )
        assert r.status_code == 422

    def test_duplicate_name_rejected(self, superuser_client: TestClient) -> None:
        superuser_client.post("/api/v1/restaurant/modifiers", json={"name": "Ice Level"})
        r = superuser_client.post("/api/v1/restaurant/modifiers", json={"name": "Ice Level"})
        assert r.status_code == 409


class TestRestaurantTables:
    def test_create_table(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/restaurant/tables",
            json={"table_number": "T01", "capacity": 4, "section": "Main Hall"},
        )
        assert r.status_code == 201
        assert r.json()["data"]["table_number"] == "T01"

    def test_duplicate_table_number_rejected(self, superuser_client: TestClient) -> None:
        superuser_client.post(
            "/api/v1/restaurant/tables",
            json={"table_number": "T99", "capacity": 2},
        )
        r = superuser_client.post(
            "/api/v1/restaurant/tables",
            json={"table_number": "T99", "capacity": 4},
        )
        assert r.status_code == 409

    def test_list_tables(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/restaurant/tables")
        assert r.status_code == 200

    def test_table_status_summary(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/restaurant/tables/status-summary")
        assert r.status_code == 200

    def test_filter_by_section(self, superuser_client: TestClient) -> None:
        superuser_client.post(
            "/api/v1/restaurant/tables",
            json={"table_number": "T-VIP-01", "capacity": 6, "section": "VIP"},
        )
        r = superuser_client.get("/api/v1/restaurant/tables?section=VIP")
        assert r.status_code == 200
