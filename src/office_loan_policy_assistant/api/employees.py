from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from office_loan_policy_assistant.core.dependencies import get_current_user
from office_loan_policy_assistant.db.database import get_db
from office_loan_policy_assistant.models.employee import Employee
from office_loan_policy_assistant.models.user import User
from office_loan_policy_assistant.schemas.auth import EmployeeProfileResponse


router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


@router.get("/me", response_model=EmployeeProfileResponse)
def get_my_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> EmployeeProfileResponse:
    """Retrieve the authenticated employee's basic profile."""

    # Retrieve the employee linked to the authenticated user
    employee = db.get(Employee, current_user.employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found",
        )

    # Return only the fields permitted by the response schema
    return EmployeeProfileResponse(
        staff_id=employee.staff_id,
        full_name=employee.full_name,
        email=employee.email,
        staff_level=employee.staff_level,
    )