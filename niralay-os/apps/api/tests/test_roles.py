from fastapi.testclient import TestClient

def test_list_roles(superuser_client: TestClient):
    response = superuser_client.get("/api/v1/roles")
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 13  # The 13 default roles

def test_create_role(superuser_client: TestClient):
    response = superuser_client.post(
        "/api/v1/roles",
        json={
            "name": "Custom Role",
            "slug": "custom_role",
            "description": "Test role",
            "permission_ids": []
        }
    )
    assert response.status_code == 201
    assert response.json()["data"]["name"] == "Custom Role"

def test_list_permissions(superuser_client: TestClient):
    response = superuser_client.get("/api/v1/permissions")
    assert response.status_code == 200
    assert len(response.json()["data"]) > 0
