from types import SimpleNamespace
from datetime import date
from office_loan_policy_assistant.services.eligibility_service import (
    check_employee_eligibility,
    check_previous_loan_repayment,
)


def test_employee_on_probation():
    """Verify employees on probation are flagged."""

    employee = SimpleNamespace(
        is_full_time=True,
        probation_completed=False,
        is_in_good_standing=True,
    )

    result = check_employee_eligibility(employee)

    assert result["meets_basic_criteria"] is False
    assert "Employee has not completed probation." in result["reasons"]



def test_previous_loan_repayment_waiting_period():
    """Verify the six-month repayment waiting period."""

    result = check_previous_loan_repayment(
        last_repayment_date=date(2026, 7, 1),
        assessment_date=date(2026, 10, 23),
    )

    assert result["meets_repayment_history_rule"] is False