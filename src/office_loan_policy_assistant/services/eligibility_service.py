from office_loan_policy_assistant.models.employee import Employee
from office_loan_policy_assistant.models.loan import Loan
from datetime import date, timedelta
from decimal import Decimal
from dateutil.relativedelta import relativedelta



def check_employee_eligibility(employee: Employee) -> dict:
    """Check basic employment eligibility for company loans."""

    reasons = []

    if not employee.is_full_time:
        reasons.append("Employee is not a full-time staff member.")

    if not employee.probation_completed:
        reasons.append("Employee has not completed probation.")

    if not employee.is_in_good_standing:
        reasons.append("Employee is not in good standing.")

    return {
        "meets_basic_criteria": len(reasons) == 0,
        "reasons": reasons,
        "note": (
            "This is a preliminary eligibility check. "
            "Outstanding loans, repayment history, guarantor "
            "requirements, and management approval must also be assessed."
        ),
    }


def check_previous_loan_repayment(
    last_repayment_date: date | None,
    assessment_date: date,
) -> dict:
    """Check the six-month waiting period after loan repayment."""

    if last_repayment_date is None:
        return {
            "meets_repayment_history_rule": None,
            "reason": "Previous loan repayment history requires verification.",
        }

    if last_repayment_date > assessment_date:
        return {
            "meets_repayment_history_rule": False,
            "reason": "The repayment date cannot be in the future.",
        }

    eligible_date = last_repayment_date + relativedelta(months=6)

    if assessment_date < eligible_date:
        return {
            "meets_repayment_history_rule": False,
            "reason": "Six months have not passed since the previous loan was repaid.",
        }

    return {
        "meets_repayment_history_rule": True,
        "reason": "The six-month repayment waiting period has been satisfied.",
    }


def check_active_loan(active_loan: Loan | None) -> dict:
    """Check whether an employee has an existing active loan."""

    if active_loan is None:
        return {
            "has_active_loan": False,
            "reason": "No active loan was found in the company loan records.",
        }

    return {
        "has_active_loan": True,
        "reason": (
            "Employee has an existing active loan. "
            "A new loan generally requires the existing loan to be settled. "
            "Management-approved top-up exceptions may apply."
        ),
    }


def check_total_outstanding_limit(
    gross_monthly_salary: Decimal,
    requested_amount: Decimal,
    existing_balance: Decimal,
) -> dict:
    """Check the total outstanding loan limit."""

    if (
        gross_monthly_salary <= 0
        or requested_amount <= 0
        or existing_balance < 0
    ):
        raise ValueError("Invalid loan or salary amount.")

    # Apply the policy's 50% annual gross salary limit
    annual_gross_salary = gross_monthly_salary * Decimal("12")
    maximum_outstanding = annual_gross_salary * Decimal("0.50")

    combined_amount = existing_balance + requested_amount

    return {
        "existing_outstanding_balance": existing_balance,
        "combined_loan_amount": combined_amount,
        "is_within_total_outstanding_limit": (
            combined_amount <= maximum_outstanding
        ),
    }