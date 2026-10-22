from decimal import Decimal, ROUND_HALF_UP

from office_loan_policy_assistant.schemas.loan import (
    LoanType,
    LoanCalculationRequest,
    LoanCalculationResponse,
)


def calculate_loan(
    request: LoanCalculationRequest,
) -> LoanCalculationResponse:
    """Calculate borrowing limits using the Office Loan Policy."""

    gross = request.gross_monthly_salary
    net = request.net_monthly_salary
    amount = request.requested_amount

    # Calculate general policy limits
    annual_gross = gross * Decimal("12")
    general_single_limit = gross * Decimal("2")
    total_outstanding_limit = annual_gross * Decimal("0.50")

    monthly_repayment_limit = (
        net / Decimal("3")
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Calculate category-specific limits
    category_limits = {
        LoanType.EMERGENCY: net * Decimal("0.50"),
        LoanType.PERSONAL: min(
            gross * Decimal("2"),
            annual_gross * Decimal("0.333"),
        ),
        LoanType.SALARY_ADVANCE: net * Decimal("0.30"),
        LoanType.DEVELOPMENT: gross * Decimal("2"),
    }

    # Apply the most restrictive applicable borrowing limit
    maximum_loan = min(
        category_limits[request.loan_type],
        general_single_limit,
        total_outstanding_limit,
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    is_within_limit = amount <= maximum_loan

    message = (
        "Requested amount is within the calculated borrowing limit."
        if is_within_limit
        else "Requested amount exceeds the calculated borrowing limit."
    )

    message += (
        " This is a preliminary assessment, not loan approval. "
        "Interest, repayment affordability, existing loans, "
        "eligibility conditions, and management exceptions "
        "require further assessment."
    )

    # Calculate principal-only repayment affordability
    repayment = calculate_repayment_affordability(
        loan_amount=amount,
        repayment_months=request.repayment_months,
        net_monthly_salary=net,
)

    # Explain the principal-only affordability result
    if repayment["is_affordable"]:
        message += (
            " The estimated principal-only monthly repayment "
            "is within the permitted salary deduction limit."
        )
    else:
        message += (
            " The estimated principal-only monthly repayment "
            "exceeds the permitted salary deduction limit."
        )

    return LoanCalculationResponse(
        loan_type=request.loan_type,
        requested_amount=amount,
        maximum_loan_amount=maximum_loan,
        repayment_months=request.repayment_months,
        monthly_repayment_limit=monthly_repayment_limit,
        is_within_loan_limit=is_within_limit,
        assessment_type="hypothetical",
        message=message,
        estimated_monthly_repayment=repayment["monthly_repayment"],
        is_principal_affordable=repayment["is_affordable"],
        repayment_calculation_note=(
            "This repayment estimate excludes interest and fees. "
            "Final affordability requires the applicable interest rate "
            "and repayment schedule."
        ),
    )


def calculate_repayment_affordability(
    loan_amount: Decimal,
    repayment_months: int,
    net_monthly_salary: Decimal,
) -> dict:
    """Check whether monthly loan repayments are affordable."""

    if loan_amount <= 0 or repayment_months <= 0 or net_monthly_salary <= 0:
        raise ValueError("Loan amount, duration, and salary must be positive.")

    # Calculate monthly repayment before interest
    monthly_repayment = (
        loan_amount / Decimal(repayment_months)
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Apply the policy's one-third salary deduction limit
    monthly_limit = (
        net_monthly_salary / Decimal("3")
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "monthly_repayment": monthly_repayment,
        "monthly_repayment_limit": monthly_limit,
        "is_affordable": monthly_repayment <= monthly_limit,
    }