from fastapi import APIRouter

from office_loan_policy_assistant.schemas.loan import (
    LoanCalculationRequest,
    LoanCalculationResponse,
)
from office_loan_policy_assistant.services.loan_service import calculate_loan


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