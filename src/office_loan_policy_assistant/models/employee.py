from datetime import date
from decimal import Decimal
from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from office_loan_policy_assistant.db.database import Base


# Define the employee database table
class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    staff_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    staff_level: Mapped[str] = mapped_column(String(20), nullable=False)
    gross_monthly_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    net_monthly_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    is_full_time: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    probation_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_in_good_standing: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_loan_repayment_date: Mapped[date | None] = mapped_column(Date, nullable=True)