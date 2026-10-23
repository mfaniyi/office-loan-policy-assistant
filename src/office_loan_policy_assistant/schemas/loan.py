from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, model_validator


class LoanType(str, Enum):
    EMERGENCY = "emergency"
    PERSONAL = "personal"
    SALARY_ADVANCE = "salary_advance"
    DEVELOPMENT = "development"


class LoanCalculationRequest(BaseModel):
    """Validate inputs for hypothetical loan calculations."""
    loan_type: LoanType
    gross_monthly_salary: Decimal = Field(gt=0)
    net_monthly_salary: Decimal = Field(gt=0)
    requested_amount: Decimal = Field(gt=0)
    repayment_months: int = Field(ge=1, le=12)
    annual_interest_rate: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    @model_validator(mode="after")
    def validate_repayment_period(self):
        """Validate repayment duration against the loan category."""

        allowed_periods = {
            LoanType.EMERGENCY: (1, 3),
            LoanType.PERSONAL: (6, 12),
            LoanType.SALARY_ADVANCE: (3, 3),
            LoanType.DEVELOPMENT: (3, 12),
        }

        minimum, maximum = allowed_periods[self.loan_type]

        if not minimum <= self.repayment_months <= maximum:
            raise ValueError(
                f"{self.loan_type.value} loans require a "
                f"repayment period between {minimum} and {maximum} months."
            )

        return self


class LoanCalculationResponse(BaseModel):
    """Represent the result of a loan calculation."""
    loan_type: LoanType
    requested_amount: Decimal
    maximum_loan_amount: Decimal
    repayment_months: int
    monthly_repayment_limit: Decimal
    is_within_loan_limit: bool
    assessment_type: str = "hypothetical"
    message: str
    estimated_monthly_repayment: Decimal
    is_principal_affordable: bool
    repayment_calculation_note: str
    interest_included: bool = False
    total_interest: Decimal | None = None
    monthly_repayment_with_interest: Decimal | None = None
    is_interest_affordable: bool | None = None


class LoanInterestRequest(BaseModel):
    """Validate inputs for illustrative interest calculations."""

    loan_type: LoanType
    principal: Decimal = Field(gt=0)
    annual_interest_rate: Decimal = Field(ge=0, le=100)
    repayment_months: int = Field(ge=1, le=12)

    @model_validator(mode="after")
    def validate_interest_rate(self):
        """Validate interest rates and repayment periods."""

        rate_limits = {
            LoanType.PERSONAL: (Decimal("5"), Decimal("10")),
            LoanType.SALARY_ADVANCE: (Decimal("7"), Decimal("9")),
            LoanType.DEVELOPMENT: (Decimal("0"), Decimal("0")),
        }

        allowed_periods = {
            LoanType.EMERGENCY: (1, 3),
            LoanType.PERSONAL: (6, 12),
            LoanType.SALARY_ADVANCE: (3, 3),
            LoanType.DEVELOPMENT: (3, 12),
        }

        minimum_months, maximum_months = allowed_periods[self.loan_type]

        if not minimum_months <= self.repayment_months <= maximum_months:
            raise ValueError(
                f"{self.loan_type.value} loans require a repayment period "
                f"between {minimum_months} and {maximum_months} months."
            )

        if self.loan_type in rate_limits:
            minimum_rate, maximum_rate = rate_limits[self.loan_type]

            if not minimum_rate <= self.annual_interest_rate <= maximum_rate:
                raise ValueError(
                    f"{self.loan_type.value} loans require an interest rate "
                    f"between {minimum_rate}% and {maximum_rate}%."
                )

        return self


class LoanInterestResponse(BaseModel):
    """Represent an illustrative loan interest calculation."""
    loan_type: LoanType
    principal: Decimal
    annual_interest_rate: Decimal
    repayment_months: int
    interest_method: str
    total_interest: Decimal
    total_repayment: Decimal
    monthly_repayment: Decimal
    calculation_note: str


class PersonalLoanAssessmentRequest(BaseModel):
    """Validate personalized loan assessment inputs."""
    loan_type: LoanType
    requested_amount: Decimal = Field(gt=0)
    repayment_months: int = Field(ge=1, le=12)
    annual_interest_rate: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
    )


class PersonalLoanAssessmentResponse(LoanCalculationResponse):
    """Include basic employee eligibility in personalized assessments."""

    meets_basic_criteria: bool
    eligibility_reasons: list[str]
    eligibility_note: str
    meets_repayment_history_rule: bool | None = None
    repayment_history_reason: str