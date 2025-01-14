from unittest.mock import AsyncMock, patch
from tests.conftest import client
from services import Category


@patch.object(Category, 'create', new_callable=AsyncMock)
def test_create_category(mock_create_category):
    mock_create_category.return_value = {"id": 1, "name": "testcategory"}

    response = client.post("/categories", json={"name": "TestCategory"},
                           headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 201
    assert response.json()["name"] == "testcategory"

    mock_create_category.assert_called_once_with(({"id": "123", "email": "testuser@example.com"}, "mock_token"),
                                                 "TestCategory")


@patch.object(Category, 'get_all', new_callable=AsyncMock)
def test_get_all_categories(mock_get_all_categories):
    mock_get_all_categories.return_value = [{"id": 1, "name": "testcategory"}]

    response = client.get("/categories", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["name"] == "testcategory"

    mock_get_all_categories.assert_called_once_with(({"id": "123", "email": "testuser@example.com"}, "mock_token"))


@patch.object(Category, 'get_by_name', new_callable=AsyncMock)
def test_get_category_by_name(mock_get_category_by_name):
    mock_get_category_by_name.return_value = {"id": 1, "name": "testcategory"}

    response = client.get("/categories/TestCategory", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    assert response.json()["name"] == "testcategory"

    mock_get_category_by_name.assert_called_once_with(({"id": "123", "email": "testuser@example.com"}, "mock_token"),
                                                      "TestCategory")


@patch.object(Category, 'delete', new_callable=AsyncMock)
def test_delete_category(mock_delete_category):
    mock_delete_category.return_value = None

    response = client.delete("/categories/TestCategory", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 204

    mock_delete_category.assert_called_once_with(({"id": "123", "email": "testuser@example.com"}, "mock_token"),
                                                 "TestCategory")
