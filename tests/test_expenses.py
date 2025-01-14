from models import ExpenseUpdate, ExpenseCreate
from unittest.mock import AsyncMock, patch
from tests.conftest import client
from services import Expense


@patch.object(Expense, 'create', new_callable=AsyncMock)
def test_create_expense(mock_create_expense):
    mock_create_expense.return_value = {"category": "testcategory", "amount": 100.0, "description": "Test Expense"}

    response = client.post("/expenses",
                           json={"category": "TestCategory", "amount": 100.0, "description": "Test Expense"},
                           headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 201
    assert response.json()["category"] == "testcategory"
    assert response.json()["amount"] == 100.0
    assert response.json()["description"] == "Test Expense"

    mock_create_expense.assert_called_once_with(
        ({"id": "123", "email": "testuser@example.com"}, "mock_token"),
        ExpenseCreate(amount=100.0, category="TestCategory", description="Test Expense")
    )


@patch.object(Expense, 'get_by_user', new_callable=AsyncMock)
def test_get_expenses(mock_get_expenses_by_user):
    mock_get_expenses_by_user.return_value = [
        {"id": 1, "category": "testcategory", "amount": 100.0, "description": "Test Expense"}]

    response = client.get("/expenses/testuser@example.com", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["category"] == "testcategory"

    mock_get_expenses_by_user.assert_called_once_with(({"id": "123", "email": "testuser@example.com"}, "mock_token"))


@patch.object(Expense, 'update', new_callable=AsyncMock)
def test_update_expense(mock_update_expense):
    mock_update_expense.return_value = {"id": 1, "category": "testcategory", "amount": 150.0,
                                        "description": "Updated Test Expense"}

    response = client.put("/expenses/1",
                          json={"category": "TestCategory", "amount": 150.0, "description": "Updated Test Expense"},
                          headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    assert response.json()["amount"] == 150.0
    assert response.json()["description"] == "Updated Test Expense"

    mock_update_expense.assert_called_once_with(
        "1",
        ExpenseUpdate(amount=150.0, category="TestCategory", description="Updated Test Expense"),
        ({"id": "123", "email": "testuser@example.com"}, "mock_token")
    )


@patch.object(Expense, 'delete', new_callable=AsyncMock)
def test_delete_expense(mock_delete_expense):
    mock_delete_expense.return_value = None

    response = client.delete("/expenses/1", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 204

    mock_delete_expense.assert_called_once_with("1", ({"id": "123", "email": "testuser@example.com"}, "mock_token"))
