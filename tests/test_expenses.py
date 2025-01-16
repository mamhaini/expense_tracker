from models import ExpenseUpdate, ExpenseCreate
from unittest.mock import AsyncMock, patch
from tests.conftest import client
from services import Expense


@patch.object(Expense, 'create', new_callable=AsyncMock)
def test_create_expense(mock_create_expense):
    mock_create_expense.return_value = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "user_id": "123e4567-e89b-12d3-a456-426614174001",
        "amount": 100.0,
        "category": "testcategory",
        "description": "Test Expense",
        "payment_method": "bank",
        "is_recurring": False,
        "currency": "USD",
        "created_at": "2023-10-01T12:00:00Z",
        "updated_at": None
    }

    response = client.post("/expenses",
                           json={"category": "TestCategory", "amount": 100.0, "description": "Test Expense"},
                           headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 201
    assert response.json()["category"] == "testcategory"
    assert response.json()["amount"] == 100.0
    assert response.json()["description"] == "Test Expense"

    mock_create_expense.assert_called_once_with(
        ({"id": "b79ab841-9bc5-426c-826e-192110dbada0",
          "email": "testuser@example.com",
          "created_at": "2025-01-15T17:24:15.541471"}, "mock_token"),
        ExpenseCreate(amount=100.0, category="TestCategory", description="Test Expense")
    )


@patch.object(Expense, 'get_by_user', new_callable=AsyncMock)
def test_get_expenses(mock_get_expenses_by_user):
    mock_get_expenses_by_user.return_value = [{
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "user_id": "123e4567-e89b-12d3-a456-426614174001",
        "amount": 100.0,
        "category": "testcategory",
        "description": "Test Expense",
        "payment_method": "bank",
        "is_recurring": False,
        "currency": "USD",
        "created_at": "2023-10-01T12:00:00Z",
        "updated_at": None
    }]

    response = client.get("/expenses/testuser@example.com", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["category"] == "testcategory"

    mock_get_expenses_by_user.assert_called_once_with(({"id": "b79ab841-9bc5-426c-826e-192110dbada0",
                                                        "email": "testuser@example.com",
                                                        "created_at": "2025-01-15T17:24:15.541471"}, "mock_token"))


@patch.object(Expense, 'update', new_callable=AsyncMock)
def test_update_expense(mock_update_expense):
    mock_update_expense.return_value = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "user_id": "123e4567-e89b-12d3-a456-426614174001",
        "amount": 150.0,
        "category": "TestCategory",
        "description": "Updated Test Expense",
        "payment_method": "bank",
        "is_recurring": False,
        "currency": "USD",
        "created_at": "2023-10-01T12:00:00Z",
        "updated_at": "2023-10-02T12:00:00Z"
    }

    response = client.put("/expenses/123e4567-e89b-12d3-a456-426614174000",
                          json={"category": "TestCategory", "amount": 150.0, "description": "Updated Test Expense"},
                          headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    assert response.json()["amount"] == 150.0
    assert response.json()["description"] == "Updated Test Expense"

    mock_update_expense.assert_called_once_with(
        "123e4567-e89b-12d3-a456-426614174000",
        ExpenseUpdate(amount=150.0, category="TestCategory", description="Updated Test Expense"),
        ({"id": "b79ab841-9bc5-426c-826e-192110dbada0",
          "email": "testuser@example.com",
          "created_at": "2025-01-15T17:24:15.541471"}, "mock_token")
    )


@patch.object(Expense, 'delete', new_callable=AsyncMock)
def test_delete_expense(mock_delete_expense):
    mock_delete_expense.return_value = None

    response = client.delete("/expenses/1", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 204

    mock_delete_expense.assert_called_once_with("1", ({"id": "b79ab841-9bc5-426c-826e-192110dbada0",
                                                       "email": "testuser@example.com",
                                                       "created_at": "2025-01-15T17:24:15.541471"}, "mock_token"))
