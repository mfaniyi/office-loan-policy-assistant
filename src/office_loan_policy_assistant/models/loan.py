from datetime import date
from decimal import Decimal
from enum import Enum

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from office_loan_policy_assistant.db.database import Base


class LoanStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DEFAULTED = "defaulted"


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )

    loan_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    principal_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    outstanding_balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default=LoanStatus.ACTIVE.value,
        nullable=False,
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )