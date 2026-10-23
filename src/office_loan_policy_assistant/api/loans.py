from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from office_loan_policy_assistant.schemas.loan import (
    LoanCalculationRequest,
    LoanCalculationResponse,
    LoanInterestRequest,
    LoanInterestResponse,
    PersonalLoanAssessmentRequest,
    PersonalLoanAssessmentResponse,
)
from office_loan_policy_assistant.services.loan_service import calculate_loan, calculate_loan_interest
from office_loan_policy_assistant.core.dependencies import get_current_user
from office_loan_policy_assistant.db.database import get_db
from office_loan_policy_assistant.models.employee import Employee
from office_loan_policy_assistant.models.user import User
from office_loan_policy_assistant.services.personal_loan_service import (
    calculate_personal_loan,
)




router = APIRouter(
    prefix="/loans",
    tags=["Loan Calculations"],
)


@router.post("/calculate", response_model=LoanCalculationResponse)
def calculate_hypothetical_loan(
    request: LoanCalculationRequest,
) -> LoanCalculationResponse:
    """Calculate a hypothetical loan without requiring authentication."""

    return calculate_loan(request)


@router.post("/interest", response_model=LoanInterestResponse)
def calculate_interest(
    request: LoanInterestRequest,
) -> LoanInterestResponse:
    """Calculate illustrative loan interest without authentication."""

    try:
        return calculate_loan_interest(request)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc


@router.post(
    "/my-assessment",
    response_model=PersonalLoanAssessmentResponse,
    responses={
        401: {"description": "Authentication required or invalid token"},
        404: {"description": "Employee profile not found"},
    },
)
def assess_my_loan(
    request: PersonalLoanAssessmentRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PersonalLoanAssessmentResponse:
    """Calculate a loan using the authenticated employee's details."""

    # Retrieve only the authenticated employee's record
    employee = db.get(Employee, current_user.employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found",
        )

    return calculate_personal_loan(
        employee=employee,
        request=request,
        db=db,
    )