from fastapi.testclient import TestClient

def test_list_users(superuser_client: TestClient):
    response = superuser_client.get("/api/v1/users")
    assert response.status_code == 200
    assert "data" in response.json()
    assert len(response.json()["data"]) >= 1

def test_create_user(superuser_client: TestClient):
    response = superuser_client.post(
        "/api/v1/users",
        json={
            "username": "new_user",
            "email": "new@niralayos.com",
            "password": "StrongPassword123!",
            "full_name": "New User"
        }
    )
    assert response.status_code == 201
    assert response.json()["data"]["username"] == "new_user"

def test_get_user(superuser_client: TestClient):
    # Get the user we just created
    list_resp = superuser_client.get("/api/v1/users?search=new_user")
    user_id = list_resp.json()["data"][0]["id"]
    
    response = superuser_client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["data"]["email"] == "new@niralayos.com"

def test_deactivate_user(superuser_client: TestClient):
    # Get the user we just created
    list_resp = superuser_client.get("/api/v1/users?search=new_user")
    user_id = list_resp.json()["data"][0]["id"]
    
    response = superuser_client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    
    # Try fetching it
    response = superuser_client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 404
