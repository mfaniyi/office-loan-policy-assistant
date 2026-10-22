from fastapi import APIRouter, HTTPException, status

from office_loan_policy_assistant.schemas.loan import (
    LoanCalculationRequest,
    LoanCalculationResponse,
    LoanInterestRequest,
    LoanInterestResponse,
)
from office_loan_policy_assistant.services.loan_service import calculate_loan, calculate_loan_interest


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