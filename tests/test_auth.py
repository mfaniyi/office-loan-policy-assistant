import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from office_loan_policy_assistant.main import app
from office_loan_policy_assistant.db.database import get_db
from office_loan_policy_assistant.services.auth_service import authenticate_user


client = TestClient(app)


# Supply a mock database session during API tests
def override_get_db():
    yield Mock()


@pytest.fixture(autouse=True)
def mock_database():
    """Provide an isolated database dependency for each test."""

    app.dependency_overrides[get_db] = override_get_db

    yield

    # Restore the application's original dependencies
    app.dependency_overrides.pop(get_db, None)


def test_login_success(monkeypatch):
    """Verify that valid credentials return a JWT."""

    # Simulate a successfully authenticated user
    mock_user = Mock()
    mock_user.id = 1

    monkeypatch.setattr(
        "office_loan_policy_assistant.api.auth.authenticate_user",
        lambda **kwargs: mock_user,
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "daniel@example.com",
            "password": "DemoPassword123!",
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert isinstance(response.json()["access_token"], str)


def test_login_invalid_credentials(monkeypatch):
    """Verify that invalid credentials are rejected."""

    # Simulate failed authentication
    monkeypatch.setattr(
        "office_loan_policy_assistant.api.auth.authenticate_user",
        lambda **kwargs: None,
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "daniel@example.com",
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_invalid_email():
    """Verify that malformed email addresses are rejected."""

    response = client.post(
        "/auth/login",
        json={
            "email": "invalid-email",
            "password": "DemoPassword123!",
        },
    )

    assert response.status_code == 422