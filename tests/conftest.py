from fastapi.testclient import TestClient
from services import User
from main import app

import pytest

client = TestClient(app)


# Mocked `validate_user` dependency
async def mock_validate_user():
    return {"id": "123", "email": "testuser@example.com"}, "mock_token"


@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    """Setup and teardown for the test module. Overrides the `validate_user` dependency with a mock."""
    app.dependency_overrides[User.validate] = mock_validate_user
    with client:
        yield
    app.dependency_overrides = {}
