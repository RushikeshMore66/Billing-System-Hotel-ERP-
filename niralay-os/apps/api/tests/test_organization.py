"""
Integration tests for Organisation Configuration API.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


class TestDepartments:
    def test_list_departments(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/organization/departments")
        assert r.status_code == 200

    def test_create_department(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/organization/departments",
            json={"name": "Security", "code": "SECURITY", "display_order": 10},
        )
        assert r.status_code == 201
        data = r.json()["data"]
        assert data["code"] == "SECURITY"

    def test_duplicate_code_rejected(self, superuser_client: TestClient) -> None:
        superuser_client.post(
            "/api/v1/organization/departments",
            json={"name": "IT Department", "code": "IT_DEPT"},
        )
        r = superuser_client.post(
            "/api/v1/organization/departments",
            json={"name": "IT Dept Dup", "code": "IT_DEPT"},
        )
        assert r.status_code == 409

    def test_cannot_delete_system_department(self, superuser_client: TestClient) -> None:
        # RECEPTION is a system department seeded in migration
        lst = superuser_client.get("/api/v1/organization/departments?search=Reception")
        items = lst.json()["items"]
        if not items:
            pytest.skip("RECEPTION department not found — seeder may not have run in test DB")
        dept_id = items[0]["id"]
        r = superuser_client.delete(f"/api/v1/organization/departments/{dept_id}")
        assert r.status_code == 403


class TestDesignations:
    def test_create_designation(self, superuser_client: TestClient) -> None:
        # First create a department to link to
        dept_r = superuser_client.post(
            "/api/v1/organization/departments",
            json={"name": "Bar", "code": "BAR_DEPT"},
        )
        dept_id = dept_r.json()["data"]["id"]
        r = superuser_client.post(
            "/api/v1/organization/designations",
            json={"name": "Bartender", "code": "BARTENDER", "department_id": dept_id},
        )
        assert r.status_code == 201

    def test_invalid_department_rejected(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/organization/designations",
            json={"name": "Ghost", "code": "GHOST_DESIG", "department_id": 999999},
        )
        assert r.status_code == 404

    def test_duplicate_code_rejected(self, superuser_client: TestClient) -> None:
        superuser_client.post(
            "/api/v1/organization/designations",
            json={"name": "Chef", "code": "CHEF"},
        )
        r = superuser_client.post(
            "/api/v1/organization/designations",
            json={"name": "Chef Dup", "code": "CHEF"},
        )
        assert r.status_code == 409


class TestGuestIDTypes:
    def test_list_guest_id_types(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/organization/guest-id-types")
        assert r.status_code == 200

    def test_create_guest_id_type(self, superuser_client: TestClient) -> None:
        r = superuser_client.post(
            "/api/v1/organization/guest-id-types",
            json={"name": "Military ID", "code": "MILITARY_ID", "requires_expiry": True},
        )
        assert r.status_code == 201

    def test_duplicate_code_rejected(self, superuser_client: TestClient) -> None:
        superuser_client.post(
            "/api/v1/organization/guest-id-types",
            json={"name": "Company ID", "code": "COMPANY_ID"},
        )
        r = superuser_client.post(
            "/api/v1/organization/guest-id-types",
            json={"name": "Company ID Dup", "code": "COMPANY_ID"},
        )
        assert r.status_code == 409
