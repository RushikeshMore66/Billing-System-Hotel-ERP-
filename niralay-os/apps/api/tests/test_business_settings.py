"""
Integration tests for Business Settings API.
"""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestBusinessSettings:
    def test_get_settings_auto_creates_defaults(self, superuser_client: TestClient) -> None:
        r = superuser_client.get("/api/v1/settings/business")
        assert r.status_code == 200
        data = r.json()["data"]
        assert "invoice_number_format" in data
        assert "timezone" in data
        assert data["decimal_precision"] == 2

    def test_update_settings(self, superuser_client: TestClient) -> None:
        r = superuser_client.patch(
            "/api/v1/settings/business",
            json={
                "invoice_number_format": "BILL-{YYYY}-{SEQ}",
                "date_format": "DD/MM/YYYY",
                "time_format": "24h",
                "decimal_precision": 2,
                "auto_backup_enabled": True,
                "auto_backup_frequency": "daily",
            },
        )
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["invoice_number_format"] == "BILL-{YYYY}-{SEQ}"
        assert data["time_format"] == "24h"
        assert data["auto_backup_enabled"] is True

    def test_invalid_date_format_rejected(self, superuser_client: TestClient) -> None:
        r = superuser_client.patch(
            "/api/v1/settings/business",
            json={"date_format": "not-a-format"},
        )
        assert r.status_code == 422

    def test_invalid_backup_frequency_rejected(self, superuser_client: TestClient) -> None:
        r = superuser_client.patch(
            "/api/v1/settings/business",
            json={"auto_backup_frequency": "hourly"},
        )
        assert r.status_code == 422

    def test_minimum_advance_pct_bounds(self, superuser_client: TestClient) -> None:
        # Over 100% should be rejected
        r = superuser_client.patch(
            "/api/v1/settings/business",
            json={"minimum_advance_payment_pct": 110},
        )
        assert r.status_code == 422

    def test_update_is_idempotent(self, superuser_client: TestClient) -> None:
        # Two GETs should return the same id (singleton)
        r1 = superuser_client.get("/api/v1/settings/business")
        r2 = superuser_client.get("/api/v1/settings/business")
        assert r1.json()["data"]["id"] == r2.json()["data"]["id"]
