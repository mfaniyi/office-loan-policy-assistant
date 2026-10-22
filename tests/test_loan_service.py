from decimal import Decimal
import pytest
from office_loan_policy_assistant.schemas.loan import LoanCalculationRequest
from office_loan_policy_assistant.services.loan_service import calculate_loan
from office_loan_policy_assistant.services.loan_service import (
    calculate_repayment_affordability,
)


@pytest.mark.parametrize(
    "loan_type, repayment_months, expected_limit",
    [
        ("emergency", 3, Decimal("165000.00")),
        ("personal", 12, Decimal("800000.00")),
        ("salary_advance", 3, Decimal("99000.00")),
        ("development", 12, Decimal("800000.00")),
    ],
)
def test_loan_category_limits(
    loan_type,
    repayment_months,
    expected_limit,
):
    """Verify borrowing limits for valid repayment periods."""

    request = LoanCalculationRequest(
        loan_type=loan_type,
        gross_monthly_salary=Decimal("400000"),
        net_monthly_salary=Decimal("330000"),
        requested_amount=Decimal("50000"),
        repayment_months=repayment_months,
    )

    result = calculate_loan(request)

    assert result.maximum_loan_amount == expected_limit
    assert result.monthly_repayment_limit == Decimal("110000.00")


def test_loan_exceeds_limit():
    """Verify that excessive loan requests are flagged."""

    request = LoanCalculationRequest(
        loan_type="personal",
        gross_monthly_salary=Decimal("400000"),
        net_monthly_salary=Decimal("330000"),
        requested_amount=Decimal("900000"),
        repayment_months=12,
    )

    result = calculate_loan(request)

    assert result.is_within_loan_limit is False
    assert result.maximum_loan_amount == Decimal("800000.00")


def test_loan_within_limit():
    """Verify that requests within the limit are identified."""

    request = LoanCalculationRequest(
        loan_type="personal",
        gross_monthly_salary=Decimal("400000"),
        net_monthly_salary=Decimal("330000"),
        requested_amount=Decimal("600000"),
        repayment_months=12,
    )

    result = calculate_loan(request)

    assert result.is_within_loan_limit is True
    assert result.assessment_type == "hypothetical"


def test_affordable_repayment():
    """Verify affordable monthly repayments."""

    result = calculate_repayment_affordability(
        loan_amount=Decimal("600000"),
        repayment_months=12,
        net_monthly_salary=Decimal("330000"),
    )

    assert result["monthly_repayment"] == Decimal("50000.00")
    assert result["monthly_repayment_limit"] == Decimal("110000.00")
    assert result["is_affordable"] is True


def test_unaffordable_repayment():
    """Verify repayments exceeding the salary limit."""

    result = calculate_repayment_affordability(
        loan_amount=Decimal("600000"),
        repayment_months=3,
        net_monthly_salary=Decimal("330000"),
    )

    assert result["monthly_repayment"] == Decimal("200000.00")
    assert result["is_affordable"] is False


@pytest.mark.parametrize(
    "loan_amount, repayment_months, net_salary",
    [
        (Decimal("0"), 12, Decimal("330000")),
        (Decimal("-50000"), 12, Decimal("330000")),
        (Decimal("600000"), 0, Decimal("330000")),
        (Decimal("600000"), 12, Decimal("0")),
    ],
)
def test_invalid_repayment_inputs(
    loan_amount,
    repayment_months,
    net_salary,
):
    """Reject invalid repayment calculation inputs."""

    with pytest.raises(ValueError):
        calculate_repayment_affordability(
            loan_amount=loan_amount,
            repayment_months=repayment_months,
            net_monthly_salary=net_salary,
        )


def test_loan_within_limit_but_unaffordable():
    """Verify borrowing limits and affordability are assessed separately."""

    request = LoanCalculationRequest(
        loan_type="personal",
        gross_monthly_salary=Decimal("400000"),
        net_monthly_salary=Decimal("330000"),
        requested_amount=Decimal("800000"),
        repayment_months=6,
    )

    result = calculate_loan(request)

    assert result.is_within_loan_limit is True
    assert result.is_principal_affordable is False
    assert result.estimated_monthly_repayment == Decimal("133333.33")


def test_loan_exceeds_limit_but_repayment_is_affordable():
    """Verify affordable repayments do not override borrowing limits."""

    request = LoanCalculationRequest(
        loan_type="personal",
        gross_monthly_salary=Decimal("400000"),
        net_monthly_salary=Decimal("330000"),
        requested_amount=Decimal("900000"),
        repayment_months=12,
    )

    result = calculate_loan(request)

    assert result.is_within_loan_limit is False
    assert result.is_principal_affordable is True
    assert result.estimated_monthly_repayment == Decimal("75000.00")