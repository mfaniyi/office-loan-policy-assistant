from fastapi.testclient import TestClient
from office_loan_policy_assistant.main import app


# Create a client for testing API endpoints
client = TestClient(app)


# Test that the home endpoint responds successfully
def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the Office Loan Policy Assistant"
    }