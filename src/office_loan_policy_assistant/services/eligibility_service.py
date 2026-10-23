from office_loan_policy_assistant.models.employee import Employee
from datetime import date, timedelta
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