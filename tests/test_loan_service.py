from decimal import Decimal
import pytest
from office_loan_policy_assistant.schemas.loan import LoanCalculationRequest
from office_loan_policy_assistant.services.loan_service import calculate_loan
from office_loan_policy_assistant.services.loan_service import (
    calculate_repayment_affordability,
)
from office_loan_policy_assistant.services.loan_service import (
    calculate_loan,
    calculate_repayment_affordability,
    calculate_flat_interest,
    calculate_reducing_balance_interest,
)
from office_loan_policy_assistant.schemas.loan import LoanInterestRequest
from office_loan_policy_assistant.services.loan_service import calculate_loan_interest
from pydantic import ValidationError

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


def test_reducing_balance_interest():
    """Verify reducing-balance interest calculations."""

    result = calculate_reducing_balance_interest(
        principal=Decimal("600000"),
        annual_rate=Decimal("10"),
        repayment_months=12,
    )

    assert result["monthly_repayment"] == Decimal("52749.53")
    assert result["total_repayment"] == Decimal("632994.36")
    assert result["interest"] == Decimal("32994.36")


def test_reducing_balance_zero_interest():
    """Verify repayment calculations without interest."""

    result = calculate_reducing_balance_interest(
        principal=Decimal("120000"),
        annual_rate=Decimal("0"),
        repayment_months=12,
    )

    assert result["monthly_repayment"] == Decimal("10000.00")
    assert result["total_repayment"] == Decimal("120000.00")
    assert result["interest"] == Decimal("0.00")


@pytest.mark.parametrize(
    "principal, annual_rate, months",
    [
        (Decimal("0"), Decimal("10"), 12),
        (Decimal("-100000"), Decimal("10"), 12),
        (Decimal("100000"), Decimal("-5"), 12),
        (Decimal("100000"), Decimal("10"), 0),
    ],
)
def test_invalid_reducing_balance_inputs(
    principal,
    annual_rate,
    months,
):
    """Reject invalid reducing-balance calculation inputs."""

    with pytest.raises(ValueError):
        calculate_reducing_balance_interest(
            principal=principal,
            annual_rate=annual_rate,
            repayment_months=months,
        )


def test_flat_vs_reducing_balance_interest():
    """Compare flat and reducing-balance interest calculations."""

    principal = Decimal("600000")
    annual_rate = Decimal("10")
    repayment_months = 12

    flat_result = calculate_flat_interest(
        principal=principal,
        annual_rate=annual_rate,
        repayment_months=repayment_months,
    )

    reducing_result = calculate_reducing_balance_interest(
        principal=principal,
        annual_rate=annual_rate,
        repayment_months=repayment_months,
    )

    assert flat_result["interest"] == Decimal("60000.00")
    assert reducing_result["interest"] == Decimal("32994.36")

    # Reducing-balance interest should be lower in this scenario
    assert reducing_result["interest"] < flat_result["interest"]

    assert reducing_result["total_repayment"] < flat_result["total_repayment"]


@pytest.mark.parametrize(
    "loan_type, principal, rate, months, method, interest",
    [
        ("personal", "600000", "10", 12, "reducing_balance", "32994.36"),
        ("salary_advance", "100000", "8", 3, "flat", "2000.00"),
        ("development", "300000", "0", 6, "interest_free", "0.00"),
    ],
)
def test_loan_interest_by_category(
    loan_type, principal, rate, months, method, interest
):
    """Verify interest calculations for supported loan categories."""

    request = LoanInterestRequest(
        loan_type=loan_type,
        principal=Decimal(principal),
        annual_interest_rate=Decimal(rate),
        repayment_months=months,
    )

    result = calculate_loan_interest(request)

    assert result.interest_method == method
    assert result.total_interest == Decimal(interest)


def test_development_loan_interest_note():
    """Verify development loans have an appropriate explanation."""

    request = LoanInterestRequest(
        loan_type="development",
        principal=Decimal("300000"),
        annual_interest_rate=Decimal("0"),
        repayment_months=6,
    )

    result = calculate_loan_interest(request)

    assert "interest-free" in result.calculation_note


def test_emergency_interest_not_supported():
    """Verify unsupported emergency interest calculations are rejected."""

    request = LoanInterestRequest(
        loan_type="emergency",
        principal=Decimal("100000"),
        annual_interest_rate=Decimal("5"),
        repayment_months=3,
    )

    with pytest.raises(ValueError):
        calculate_loan_interest(request)


@pytest.mark.parametrize(
    "loan_type, invalid_rate",
    [
        ("personal", "4"),
        ("personal", "11"),
        ("salary_advance", "6"),
        ("salary_advance", "10"),
        ("development", "5"),
    ],
)
def test_invalid_loan_interest_rates(loan_type, invalid_rate):
    """Reject interest rates outside category limits."""

    with pytest.raises(ValidationError):
        LoanInterestRequest(
            loan_type=loan_type,
            principal=Decimal("100000"),
            annual_interest_rate=Decimal(invalid_rate),
            repayment_months=12,
        )


@pytest.mark.parametrize(
    "loan_type, rate, months",
    [
        ("emergency", "5", 6),
        ("personal", "10", 3),
        ("salary_advance", "8", 6),
        ("development", "0", 2),
    ],
)
def test_invalid_interest_repayment_periods(loan_type, rate, months):
    """Reject interest calculations with invalid repayment periods."""

    with pytest.raises(ValidationError):
        LoanInterestRequest(
            loan_type=loan_type,
            principal=Decimal("100000"),
            annual_interest_rate=Decimal(rate),
            repayment_months=months,
        )