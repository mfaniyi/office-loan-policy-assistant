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