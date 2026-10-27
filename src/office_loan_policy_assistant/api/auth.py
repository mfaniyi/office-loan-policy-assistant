from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from office_loan_policy_assistant.db.database import get_db
from office_loan_policy_assistant.core.security import create_access_token
from office_loan_policy_assistant.schemas.auth import (
    LoginRequest,
    TokenResponse,
)
from office_loan_policy_assistant.services.auth_service import authenticate_user
from office_loan_policy_assistant.core.rate_limit import limiter


# Create a router for authentication endpoints
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# Define the employee login endpoint
@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    credentials: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    """Authenticate an employee and issue an access token."""

    # Verify the employee's login credentials
    user = authenticate_user(
        db=db,
        email=str(credentials.email),
        password=credentials.password,
    )

    # Return a generic error for invalid credentials
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate a token for the authenticated user
    access_token = create_access_token(user_id=user.id)

    # Return the signed authentication token
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )