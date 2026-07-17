from fastapi.testclient import TestClient

def test_login_success(client: TestClient, superuser):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@niralayos.com", "password": "Admin@NiralayOS2024!"}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "access_token" in data
    assert "refresh_token" in data

def test_login_failure(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@niralayos.com", "password": "wrong"}
    )
    assert response.status_code == 401

def test_get_me(superuser_client: TestClient):
    response = superuser_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["data"]["email"] == "admin@niralayos.com"

def test_logout(superuser_client: TestClient):
    response = superuser_client.post("/api/v1/auth/logout")
    assert response.status_code == 200
