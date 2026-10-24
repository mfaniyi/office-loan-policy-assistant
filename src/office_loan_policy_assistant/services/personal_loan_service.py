from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from office_loan_policy_assistant.models.employee import Employee
from office_loan_policy_assistant.services.loan_service import calculate_loan
from office_loan_policy_assistant.schemas.loan import (
    LoanCalculationRequest,
    LoanCalculationResponse,
    PersonalLoanAssessmentRequest,
    PersonalLoanAssessmentResponse,
)
from office_loan_policy_assistant.services.eligibility_service import (
    check_employee_eligibility,
    check_previous_loan_repayment,
    check_active_loan,
    check_total_outstanding_limit,
)
from office_loan_policy_assistant.services.loan_record_service import (
    get_active_loan,
)



def calculate_personal_loan(
    employee: Employee,
    request: PersonalLoanAssessmentRequest,
    db: Session,
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

    # Retrieve the employee's active company loan
    active_loan = get_active_loan(
        db=db,
        employee_id=employee.id,
    )

    active_loan_check = check_active_loan(active_loan)

    # Calculate the outstanding balance using available company loan records
    existing_balance = (
        active_loan.outstanding_balance
        if active_loan is not None
        else Decimal("0")
    )

    outstanding_check = check_total_outstanding_limit(
        gross_monthly_salary=employee.gross_monthly_salary,
        requested_amount=request.requested_amount,
        existing_balance=existing_balance,
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

    # Explain restrictions when an active company loan exists
    if active_loan_check["has_active_loan"]:
        message += (
            " An active company loan was found. "
            "A new loan generally requires the existing loan to be settled. "
            "Management-approved top-up exceptions may apply."
        )

    # Explain when combined borrowing exceeds the policy limit
    if not outstanding_check["is_within_total_outstanding_limit"]:
        message += (
            " The combined outstanding loan amount exceeds "
            "'50%' of the employee's annual gross salary. "
            "The requested amount does not satisfy this borrowing limit."
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
        has_active_loan=active_loan_check["has_active_loan"],
        active_loan_reason=active_loan_check["reason"],
        existing_outstanding_balance=outstanding_check[
            "existing_outstanding_balance"
        ],
        combined_loan_amount=outstanding_check["combined_loan_amount"],
        is_within_total_outstanding_limit=outstanding_check[
            "is_within_total_outstanding_limit"
        ],        
    )