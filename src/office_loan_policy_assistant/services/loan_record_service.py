from sqlalchemy import select
from sqlalchemy.orm import Session

from office_loan_policy_assistant.models.loan import Loan, LoanStatus


def get_active_loan(
    db: Session,
    employee_id: int,
) -> Loan | None:
    """Retrieve an employee's active loan, if one exists."""

    statement = select(Loan).where(
        Loan.employee_id == employee_id,
        Loan.status == LoanStatus.ACTIVE.value,
    )

    return db.scalar(statement)