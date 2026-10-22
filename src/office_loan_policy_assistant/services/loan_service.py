from decimal import Decimal, ROUND_HALF_UP
from office_loan_policy_assistant.schemas.loan import (
    LoanType,
    LoanCalculationRequest,
    LoanCalculationResponse,
)
from office_loan_policy_assistant.schemas.loan import (
    LoanInterestRequest,
    LoanInterestResponse,
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
        "Existing loans, eligibility conditions, and management "
        "exceptions require further assessment."
    )

    # Calculate principal-only repayment affordability
    repayment = calculate_repayment_affordability(
        loan_amount=amount,
        repayment_months=request.repayment_months,
        net_monthly_salary=net,
)

    interest_included = False
    total_interest = None
    monthly_repayment_with_interest = None
    is_interest_affordable = None

    if request.annual_interest_rate is not None:
        interest_request = LoanInterestRequest(
            loan_type=request.loan_type,
            principal=amount,
            annual_interest_rate=request.annual_interest_rate,
            repayment_months=request.repayment_months,
        )

        interest_result = calculate_loan_interest(interest_request)

        interest_included = True
        total_interest = interest_result.total_interest
        monthly_repayment_with_interest = interest_result.monthly_repayment
        is_interest_affordable = (
            monthly_repayment_with_interest <= repayment["monthly_repayment_limit"]
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

    # Explain interest-inclusive affordability when available
    if interest_included:
        if is_interest_affordable:
            message += (
                " The illustrative interest-inclusive monthly repayment "
                "is within the permitted salary deduction limit."
            )
        else:
            message += (
                " The illustrative interest-inclusive monthly repayment "
                "exceeds the permitted salary deduction limit."
            )

        message += (
            " The interest calculation assumes an annual rate. "
            "The official rate basis and applicable fees require confirmation."
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
        interest_included=interest_included,
        total_interest=total_interest,
        monthly_repayment_with_interest=monthly_repayment_with_interest,
        is_interest_affordable=is_interest_affordable,
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


def calculate_flat_interest(
    principal: Decimal,
    annual_rate: Decimal,
    repayment_months: int,
) -> dict:
    """Calculate flat interest using an annual interest rate."""

    if principal <= 0 or annual_rate < 0 or repayment_months <= 0:
        raise ValueError("Invalid interest calculation inputs.")

    # Calculate interest proportionally to the repayment duration
    interest = (
        principal
        * (annual_rate / Decimal("100"))
        * (Decimal(repayment_months) / Decimal("12"))
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    total_repayment = principal + interest

    monthly_repayment = (
        total_repayment / Decimal(repayment_months)
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "interest": interest,
        "total_repayment": total_repayment,
        "monthly_repayment": monthly_repayment,
    }


def calculate_reducing_balance_interest(
    principal: Decimal,
    annual_rate: Decimal,
    repayment_months: int,
) -> dict:
    """Calculate equal monthly repayments using reducing-balance interest."""

    if principal <= 0 or annual_rate < 0 or repayment_months <= 0:
        raise ValueError("Invalid interest calculation inputs.")

    if annual_rate == 0:
        monthly_repayment = principal / Decimal(repayment_months)
    else:
        # Convert annual interest into a monthly rate
        monthly_rate = annual_rate / Decimal("100") / Decimal("12")

        factor = (Decimal("1") + monthly_rate) ** repayment_months

        # Calculate the fixed monthly instalment
        monthly_repayment = (
            principal * monthly_rate * factor / (factor - Decimal("1"))
        )

    monthly_repayment = monthly_repayment.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    total_repayment = monthly_repayment * Decimal(repayment_months)

    total_interest = total_repayment - principal

    return {
        "interest": total_interest,
        "total_repayment": total_repayment,
        "monthly_repayment": monthly_repayment,
    }


def calculate_loan_interest(
    request: LoanInterestRequest,
) -> LoanInterestResponse:
    """Calculate illustrative interest based on loan category."""

    if request.loan_type == LoanType.PERSONAL:
        result = calculate_reducing_balance_interest(
            request.principal,
            request.annual_interest_rate,
            request.repayment_months,
        )
        method = "reducing_balance"

    elif request.loan_type == LoanType.SALARY_ADVANCE:
        result = calculate_flat_interest(
            request.principal,
            request.annual_interest_rate,
            request.repayment_months,
        )
        method = "flat"

    elif request.loan_type == LoanType.DEVELOPMENT:
        result = calculate_flat_interest(
            request.principal,
            Decimal("0"),
            request.repayment_months,
        )
        method = "interest_free"

    else:
        raise ValueError(
            "Emergency loan interest calculations are not yet supported."
        )

    # Explain the calculation method based on the loan category
    if request.loan_type == LoanType.DEVELOPMENT:
        calculation_note = (
            "Development loans are interest-free under the Office Loan Policy. "
            "Monthly repayments are calculated by dividing the principal "
            "equally across the repayment period."
        )
    else:
        calculation_note = (
            "Illustrative calculation using an annual interest rate. "
            "The official rate basis and repayment convention "
            "require confirmation."
        )

    return LoanInterestResponse(
        loan_type=request.loan_type,
        principal=request.principal,
        annual_interest_rate=(
            Decimal("0")
            if request.loan_type == LoanType.DEVELOPMENT
            else request.annual_interest_rate
        ),
        repayment_months=request.repayment_months,
        interest_method=method,
        total_interest=result["interest"],
        total_repayment=result["total_repayment"],
        monthly_repayment=result["monthly_repayment"],
        calculation_note=calculation_note,
    )