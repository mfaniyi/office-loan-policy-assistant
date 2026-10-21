from sqlalchemy import select
from sqlalchemy.orm import Session
from office_loan_policy_assistant.core.security import verify_password
from office_loan_policy_assistant.models.user import User


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:
    """Authenticate an employee using email and password."""
    normalized_email = email.strip().lower()
    statement = select(User).where(
        User.email == normalized_email
    )

    user = db.scalar(statement)

    # Reject unknown or inactive accounts
    if user is None or not user.is_active:
        return None

    # Verify the supplied password against its stored hash
    if not verify_password(password, user.hashed_password):
        return None

    # Return the authenticated user
    return user