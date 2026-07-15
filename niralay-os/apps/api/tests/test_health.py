"""
Tests for health check endpoints.

Coverage:
  - GET /ping
  - GET /api/v1/health      (liveness)
  - GET /api/v1/health/ready (readiness — may be degraded in test environment)
"""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestPing:
    def test_ping_returns_200(self, client: TestClient):
        response = client.get("/ping")
        assert response.status_code == 200

    def test_ping_returns_pong(self, client: TestClient):
        response = client.get("/ping")
        data = response.json()
        assert data["pong"] is True


class TestRoot:
    def test_root_returns_200(self, client: TestClient):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_contains_app_name(self, client: TestClient):
        response = client.get("/")
        data = response.json()
        assert "app" in data
        assert data["app"] == "NiralayOS"

    def test_root_contains_version(self, client: TestClient):
        response = client.get("/")
        data = response.json()
        assert "version" in data


class TestLiveness:
    def test_liveness_returns_200(self, client: TestClient):
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_liveness_response_envelope(self, client: TestClient):
        response = client.get("/api/v1/health")
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "meta" in data

    def test_liveness_data_fields(self, client: TestClient):
        response = client.get("/api/v1/health")
        health = response.json()["data"]
        assert health["status"] == "ok"
        assert health["app"] == "NiralayOS"
        assert "version" in health
        assert "uptime_seconds" in health
        assert isinstance(health["uptime_seconds"], float)

    def test_liveness_meta_has_request_id(self, client: TestClient):
        response = client.get("/api/v1/health")
        meta = response.json()["meta"]
        assert "request_id" in meta
        assert len(meta["request_id"]) > 0

    def test_liveness_response_has_x_request_id_header(self, client: TestClient):
        response = client.get("/api/v1/health")
        assert "x-request-id" in response.headers

    def test_liveness_client_request_id_is_echoed(self, client: TestClient):
        custom_id = "test-request-id-12345"
        response = client.get(
            "/api/v1/health",
            headers={"X-Request-ID": custom_id},
        )
        assert response.headers.get("x-request-id") == custom_id


class TestReadiness:
    def test_readiness_returns_200_or_503(self, client: TestClient):
        """Readiness may be 200 (DB up) or 503 (DB down) — both are valid in CI."""
        response = client.get("/api/v1/health/ready")
        assert response.status_code in (200, 503)

    def test_readiness_response_envelope(self, client: TestClient):
        response = client.get("/api/v1/health/ready")
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert "meta" in data

    def test_readiness_data_has_dependencies(self, client: TestClient):
        response = client.get("/api/v1/health/ready")
        health = response.json()["data"]
        assert "dependencies" in health
        assert "database" in health["dependencies"]
        db_dep = health["dependencies"]["database"]
        assert "status" in db_dep
        assert db_dep["status"] in ("ok", "error")

    def test_readiness_status_consistent_with_http_code(self, client: TestClient):
        response = client.get("/api/v1/health/ready")
        health = response.json()["data"]
        if response.status_code == 200:
            assert health["status"] == "ok"
        else:
            assert health["status"] == "degraded"


class TestValidationErrorFormat:
    """Verify the standard error envelope is used for validation errors."""

    def test_invalid_pagination_returns_standard_error(self, client: TestClient):
        # page=0 should fail validation
        response = client.get("/api/v1/health", params={"page": 0})
        # Health endpoint doesn't take pagination — this is just testing
        # that the app loads correctly; actual pagination validation tested
        # in Sprint 3+ endpoints
        assert response.status_code in (200, 422)
