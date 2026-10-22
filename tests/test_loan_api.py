import pytest
from fastapi.testclient import TestClient
from office_loan_policy_assistant.main import app


client = TestClient(app)


def test_public_loan_calculation():
    """Verify visitors can calculate loans without authentication."""

    response = client.post(
        "/loans/calculate",
        json={
            "loan_type": "personal",
            "gross_monthly_salary": 400000,
            "net_monthly_salary": 330000,
            "requested_amount": 600000,
            "repayment_months": 12,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["maximum_loan_amount"] == "800000.00"
    assert data["monthly_repayment_limit"] == "110000.00"
    assert data["is_within_loan_limit"] is True
    assert data["assessment_type"] == "hypothetical"
    # Verify the principal-only repayment estimate
    assert data["estimated_monthly_repayment"] == "50000.00"
    assert data["is_principal_affordable"] is True
    assert "excludes interest and fees" in data["repayment_calculation_note"]
    assert "within the permitted salary deduction limit" in data["message"]

def test_invalid_loan_amount():
    """Verify negative loan amounts are rejected."""

    response = client.post(
        "/loans/calculate",
        json={
            "loan_type": "personal",
            "gross_monthly_salary": 400000,
            "net_monthly_salary": 330000,
            "requested_amount": -50000,
            "repayment_months": 12,
        },
    )

    assert response.status_code == 422


def test_invalid_loan_category():
    """Verify unsupported loan categories are rejected."""

    response = client.post(
        "/loans/calculate",
        json={
            "loan_type": "business",
            "gross_monthly_salary": 400000,
            "net_monthly_salary": 330000,
            "requested_amount": 50000,
            "repayment_months": 12,
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("gross_monthly_salary", 0),
        ("net_monthly_salary", -1000),
        ("requested_amount", 0),
        ("repayment_months", 0),
        ("repayment_months", 13),
    ],
)
def test_invalid_loan_inputs(field, invalid_value):
    """Verify invalid financial inputs are rejected."""

    payload = {
        "loan_type": "personal",
        "gross_monthly_salary": 400000,
        "net_monthly_salary": 330000,
        "requested_amount": 600000,
        "repayment_months": 12,
    }

    # Replace one valid field with an invalid value
    payload[field] = invalid_value

    response = client.post(
        "/loans/calculate",
        json=payload,
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "loan_type, repayment_months",
    [
        ("emergency", 6),
        ("personal", 3),
        ("salary_advance", 6),
        ("development", 2),
    ],
)
def test_invalid_repayment_periods(loan_type, repayment_months):
    """Reject repayment periods outside policy limits."""

    payload = {
        "loan_type": loan_type,
        "gross_monthly_salary": 400000,
        "net_monthly_salary": 330000,
        "requested_amount": 50000,
        "repayment_months": repayment_months,
    }

    response = client.post("/loans/calculate", json=payload)

    assert response.status_code == 422


def test_unaffordable_loan_repayment():
    """Verify the API identifies unaffordable repayments."""

    response = client.post(
        "/loans/calculate",
        json={
            "loan_type": "personal",
            "gross_monthly_salary": 400000,
            "net_monthly_salary": 330000,
            "requested_amount": 800000,
            "repayment_months": 6,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["estimated_monthly_repayment"] == "133333.33"
    assert data["monthly_repayment_limit"] == "110000.00"
    assert data["is_principal_affordable"] is False
    assert data["is_within_loan_limit"] is True
    assert "exceeds the permitted salary deduction limit" in data["message"]