from pydantic import BaseModel, EmailStr, Field


# Define the employee login request
class LoginRequest(BaseModel):
    """Validate employee login credentials."""

    email: EmailStr
    password: str = Field(min_length=1)


# Define the authentication response
class TokenResponse(BaseModel):
    """Describe the token returned after successful login."""

    access_token: str
    token_type: str = "bearer"


# Define the public employee profile response
class EmployeeProfileResponse(BaseModel):
    """Return employee identity details without salary information."""

    staff_id: str
    full_name: str
    email: EmailStr
    staff_level: str