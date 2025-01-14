from unittest.mock import AsyncMock, patch
from tests.conftest import client
from services import UserService


@patch.object(UserService, 'register_user', new_callable=AsyncMock)
def test_register_user(mock_register_user):
    mock_register_user.return_value = {"id": "123", "email": "testuser@example.com"}
    response = client.post("/register", json={"email": "testuser@example.com", "password": "password123"})
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["email"] == "testuser@example.com"


@patch.object(UserService, 'login_user', new_callable=AsyncMock)
def test_login_user(mock_login_user):
    mock_login_user.return_value = {"access_token": "fake_token"}
    client.post("/register", json={"email": "testuser@example.com", "password": "password123"})
    response = client.post("/login", json={"email": "testuser@example.com", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()


@patch.object(UserService, 'validate_user', new_callable=AsyncMock)
@patch.object(UserService, 'login_user', new_callable=AsyncMock)
@patch.object(UserService, 'register_user', new_callable=AsyncMock)
def test_get_user_by_email(mock_register_user, mock_login_user, mock_validate_user):
    mock_register_user.return_value = {"id": "123", "email": "testuser@example.com"}
    mock_login_user.return_value = {"access_token": "fake_token"}
    mock_validate_user.return_value = ({"id": "123", "email": "testuser@example.com"}, "mock_token")

    client.post("/register", json={"email": "testuser@example.com", "password": "password123"})
    login_response = client.post("/login", json={"email": "testuser@example.com", "password": "password123"})

    login_response_json = login_response.json()
    assert "access_token" in login_response_json, "Login response does not contain access_token"
    access_token = login_response_json["access_token"]

    response = client.get("/users/testuser@example.com", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == "testuser@example.com"


@patch.object(UserService, 'delete_user', new_callable=AsyncMock)
@patch.object(UserService, 'login_user', new_callable=AsyncMock)
def test_delete_user(mock_login_user, mock_delete_user):
    mock_delete_user.return_value = None
    mock_login_user.return_value = {"access_token": "fake_token"}
    client.post("/register", json={"email": "testuser@example.com", "password": "password123"})
    login_response = client.post("/login", json={"email": "testuser@example.com", "password": "password123"})
    access_token = login_response.json()["access_token"]
    response = client.delete("/users/testuser@example.com", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 204
