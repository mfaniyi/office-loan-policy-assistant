from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch
from office_loan_policy_assistant.schemas.loan import (
    PersonalLoanAssessmentRequest,
)
from office_loan_policy_assistant.services.personal_loan_service import (
    calculate_personal_loan,
)


def test_personal_loan_uses_employee_salary():
    """Verify personalized calculations use stored employee salary."""

    # Simulate a fictional employee's stored financial details
    employee = SimpleNamespace(
        id=1,
        gross_monthly_salary=Decimal("250000"),
        net_monthly_salary=Decimal("210000"),
        is_full_time=True,
        probation_completed=True,
        is_in_good_standing=True,
        last_loan_repayment_date=None,
    )

    request = PersonalLoanAssessmentRequest(
        loan_type="personal",
        requested_amount=Decimal("300000"),
        repayment_months=12,
        annual_interest_rate=Decimal("10"),
    )

    # Simulate an employee with no active company loan
    with patch(
        "office_loan_policy_assistant.services.personal_loan_service.get_active_loan",
        return_value=None,
    ):
        result = calculate_personal_loan(
            employee=employee,
            request=request,
            db=Mock(),
        )

    assert result.maximum_loan_amount == Decimal("500000.00")
    assert result.monthly_repayment_limit == Decimal("70000.00")
    assert result.assessment_type == "personalized"
    assert result.is_interest_affordable is True
    assert result.has_active_loan is False
    assert "No active loan was found" in result.active_loan_reason
    assert result.existing_outstanding_balance == Decimal("0")
    assert result.combined_loan_amount == Decimal("300000")
    assert result.is_within_total_outstanding_limit is True
    assert result.repaid_amount is None
    assert result.repayment_percentage is None
    assert result.meets_topup_repayment_rule is None
    assert result.requires_management_approval is None