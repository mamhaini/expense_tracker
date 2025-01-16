from fastapi.testclient import TestClient
from services import User
from main import app

import pytest

client = TestClient(app)


# Mocked `validate_user` dependency
async def mock_validate_user():
    return {"id": "b79ab841-9bc5-426c-826e-192110dbada0", "email": "testuser@example.com",
            "created_at": "2025-01-15T17:24:15.541471"}, "mock_token"


@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    """Setup and teardown for the test module. Overrides the `validate_user` dependency with a mock."""
    app.dependency_overrides[User.validate] = mock_validate_user
    with client:
        yield
    app.dependency_overrides = {}
