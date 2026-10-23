from decimal import Decimal
from sqlalchemy import select
from datetime import date
from office_loan_policy_assistant.core.security import hash_password
from office_loan_policy_assistant.db.database import SessionLocal
from office_loan_policy_assistant.models.employee import Employee
from office_loan_policy_assistant.models.user import User
from office_loan_policy_assistant.models.loan import Loan, LoanStatus


# Fictional employee records for capstone testing
SAMPLE_EMPLOYEES = [
    {
        "staff_id": "EMP001",
        "full_name": "Daniel Adeyemi",
        "email": "daniel@example.com",
        "staff_level": "L1",
        "gross_salary": "250000.00",
        "net_salary": "210000.00",
        "probation_completed": True,
    },
    {
        "staff_id": "EMP002",
        "full_name": "Amara Okafor",
        "email": "amara@example.com",
        "staff_level": "L2",
        "gross_salary": "400000.00",
        "net_salary": "330000.00",
        "probation_completed": True,
    },
    {
        "staff_id": "EMP003",
        "full_name": "Tunde Bakare",
        "email": "tunde@example.com",
        "staff_level": "L3",
        "gross_salary": "650000.00",
        "net_salary": "520000.00",
        "probation_completed": False,
    },
]


def seed_employees() -> None:
    """Insert fictional employees and their login accounts."""

    with SessionLocal() as db:
        for record in SAMPLE_EMPLOYEES:
            # Avoid inserting duplicate employee records
            existing = db.scalar(
                select(Employee).where(
                    Employee.staff_id == record["staff_id"]
                )
            )

            if existing:
                continue

            employee = Employee(
                staff_id=record["staff_id"],
                full_name=record["full_name"],
                email=record["email"],
                staff_level=record["staff_level"],
                gross_monthly_salary=Decimal(record["gross_salary"]),
                net_monthly_salary=Decimal(record["net_salary"]),
                is_full_time=True,
                probation_completed=record["probation_completed"],
                is_in_good_standing=True,
            )

            db.add(employee)
            db.flush()

            # Create an authentication account linked to the employee
            user = User(
                email=record["email"],
                hashed_password=hash_password("DemoPassword123!"),
                employee_id=employee.id,
                is_active=True,
            )

            db.add(user)

        # Save employee and user records together
        db.commit()

    print("Employee seeding completed successfully.")


def seed_sample_loan() -> None:
    """Create a fictional active loan for testing."""

    with SessionLocal() as db:
        employee = db.scalar(
            select(Employee).where(Employee.staff_id == "EMP002")
        )

        if employee is None:
            print("Sample employee EMP002 not found.")
            return

        # Prevent duplicate active loan records
        existing_loan = db.scalar(
            select(Loan).where(
                Loan.employee_id == employee.id,
                Loan.status == LoanStatus.ACTIVE.value,
            )
        )

        if existing_loan is not None:
            print("Sample active loan already exists.")
            return

        loan = Loan(
            employee_id=employee.id,
            loan_type="personal",
            principal_amount=Decimal("400000.00"),
            outstanding_balance=Decimal("250000.00"),
            status=LoanStatus.ACTIVE.value,
            start_date=date(2026, 8, 1),
            end_date=None,
        )

        db.add(loan)
        db.commit()

        print("Sample active loan created successfully.")


if __name__ == "__main__":
    seed_employees()
    seed_sample_loan()