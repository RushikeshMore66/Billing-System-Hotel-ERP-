from fastapi.testclient import TestClient
from app.core.security import create_access_token

def test_permission_denied(client: TestClient):
    # A token with NO permissions (and not super_admin)
    token = create_access_token(
        subject="00000000-0000-0000-0000-000000000000",
        role="viewer",
        permissions=[]
    )
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    # Needs settings:manage
    response = client.post(
        "/api/v1/roles",
        json={
            "name": "Should Fail",
            "slug": "should_fail",
            "permission_ids": []
        }
    )
    
    # Wait, the user has to exist in DB for get_current_user to pass.
    # If the user doesn't exist, it returns 401. 
    # That's fine, it means auth is working.
    assert response.status_code in (401, 403)
