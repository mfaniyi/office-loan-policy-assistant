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


def test_public_interest_calculation():
    """Verify visitors can calculate illustrative loan interest."""

    response = client.post(
        "/loans/interest",
        json={
            "loan_type": "personal",
            "principal": 600000,
            "annual_interest_rate": 10,
            "repayment_months": 12,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["interest_method"] == "reducing_balance"
    assert data["total_interest"] == "32994.36"
    assert data["total_repayment"] == "632994.36"
    assert data["monthly_repayment"] == "52749.53"


def test_salary_advance_interest_api():
    """Verify flat interest calculations for salary advances."""

    response = client.post(
        "/loans/interest",
        json={
            "loan_type": "salary_advance",
            "principal": 100000,
            "annual_interest_rate": 8,
            "repayment_months": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["interest_method"] == "flat"
    assert data["total_interest"] == "2000.00"
    assert data["total_repayment"] == "102000.00"
    assert data["monthly_repayment"] == "34000.00"


def test_development_loan_interest_api():
    """Verify development loans are interest-free."""

    response = client.post(
        "/loans/interest",
        json={
            "loan_type": "development",
            "principal": 300000,
            "annual_interest_rate": 0,
            "repayment_months": 6,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["interest_method"] == "interest_free"
    assert data["total_interest"] == "0.00"
    assert data["total_repayment"] == "300000.00"
    assert data["monthly_repayment"] == "50000.00"
    assert "interest-free" in data["calculation_note"]


def test_emergency_loan_interest_not_supported():
    """Verify unsupported emergency interest calculations are rejected."""

    response = client.post(
        "/loans/interest",
        json={
            "loan_type": "emergency",
            "principal": 100000,
            "annual_interest_rate": 5,
            "repayment_months": 3,
        },
    )

    assert response.status_code == 422
    assert (
        response.json()["detail"]
        == "Emergency loan interest calculations are not yet supported."
    )


@pytest.mark.parametrize(
    "loan_type, invalid_rate, months",
    [
        ("personal", 4, 12),
        ("personal", 11, 12),
        ("salary_advance", 6, 3),
        ("salary_advance", 10, 3),
        ("development", 5, 6),
    ],
)
def test_invalid_interest_rates_api(loan_type, invalid_rate, months):
    """Reject interest rates outside the permitted category ranges."""

    response = client.post(
        "/loans/interest",
        json={
            "loan_type": loan_type,
            "principal": 100000,
            "annual_interest_rate": invalid_rate,
            "repayment_months": months,
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "loan_type, rate, months",
    [
        ("emergency", 5, 6),
        ("personal", 10, 3),
        ("salary_advance", 8, 6),
        ("development", 0, 2),
    ],
)
def test_invalid_interest_repayment_periods_api(
    loan_type, rate, months
):
    """Reject interest requests with invalid repayment periods."""

    response = client.post(
        "/loans/interest",
        json={
            "loan_type": loan_type,
            "principal": 100000,
            "annual_interest_rate": rate,
            "repayment_months": months,
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "invalid_principal",
    [0, -100000],
)
def test_invalid_interest_principal_api(invalid_principal):
    """Reject zero and negative principal amounts."""

    response = client.post(
        "/loans/interest",
        json={
            "loan_type": "personal",
            "principal": invalid_principal,
            "annual_interest_rate": 10,
            "repayment_months": 12,
        },
    )

    assert response.status_code == 422


def test_interest_inclusive_loan_calculation():
    """Verify borrowing limits and interest-inclusive affordability."""

    response = client.post(
        "/loans/calculate",
        json={
            "loan_type": "personal",
            "gross_monthly_salary": 400000,
            "net_monthly_salary": 330000,
            "requested_amount": 600000,
            "repayment_months": 12,
            "annual_interest_rate": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["maximum_loan_amount"] == "800000.00"
    assert data["interest_included"] is True
    assert data["total_interest"] == "32994.36"
    assert data["monthly_repayment_with_interest"] == "52749.53"
    assert data["is_interest_affordable"] is True
    assert data["assessment_type"] == "hypothetical"