from office_loan_policy_assistant.models.employee import Employee
from office_loan_policy_assistant.schemas.loan import (
    LoanCalculationRequest,
    LoanCalculationResponse,
    PersonalLoanAssessmentRequest,
    PersonalLoanAssessmentResponse,
)
from datetime import date
from office_loan_policy_assistant.services.eligibility_service import (
    check_employee_eligibility,
    check_previous_loan_repayment,
)
from office_loan_policy_assistant.services.loan_service import calculate_loan


def calculate_personal_loan(
    employee: Employee,
    request: PersonalLoanAssessmentRequest,
) -> PersonalLoanAssessmentResponse:
    """Calculate a personalized loan and assess basic eligibility."""

    calculation_request = LoanCalculationRequest(
        loan_type=request.loan_type,
        gross_monthly_salary=employee.gross_monthly_salary,
        net_monthly_salary=employee.net_monthly_salary,
        requested_amount=request.requested_amount,
        repayment_months=request.repayment_months,
        annual_interest_rate=request.annual_interest_rate,
    )

    calculation = calculate_loan(calculation_request)

    # Check employment eligibility separately from financial calculations
    eligibility = check_employee_eligibility(employee)

    # Check the six-month waiting period using the employee's repayment history
    repayment_history = check_previous_loan_repayment(
        last_repayment_date=employee.last_loan_repayment_date,
        assessment_date=date.today(),
    )
    
    # Explain unmet eligibility requirements
    message = calculation.message

    if not eligibility["meets_basic_criteria"]:
        message += (
            " However, the employee does not meet all basic employment "
            "eligibility requirements. Review the eligibility reasons "
            "below. Management-approved exceptions may apply."
        )

    # Explain repayment history requirements
    if repayment_history["meets_repayment_history_rule"] is None:
        message += (
            " Previous loan repayment history is unverified. "
            "HR or Finance must confirm this requirement."
        )
    elif repayment_history["meets_repayment_history_rule"] is False:
        message += (
            " The previous loan repayment waiting-period requirement "
            "has not been satisfied."
        )

    return PersonalLoanAssessmentResponse(
        **calculation.model_dump(exclude={"assessment_type", "message"}),
        assessment_type="personalized",
        message=message,
        meets_basic_criteria=eligibility["meets_basic_criteria"],
        eligibility_reasons=eligibility["reasons"],
        eligibility_note=eligibility["note"],
        meets_repayment_history_rule=repayment_history[
            "meets_repayment_history_rule"
        ],
        repayment_history_reason=repayment_history["reason"],        
    )