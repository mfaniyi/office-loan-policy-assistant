import jwt
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError
from office_loan_policy_assistant.core.config import settings


# Initialize the recommended password hashing configuration
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Generate a secure hash from a plaintext password."""

    # Hash the password before storing it
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Verify a password against its stored hash."""

    # Return True only when the password matches
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(user_id: int) -> str:
    """Generate a signed JWT for an authenticated user."""

    # Calculate when the token expires
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Store only the user identifier and expiration
    payload = {
        "sub": str(user_id),
        "exp": expires_at,
    }

    # Sign the token using our configured secret
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> int | None:
    """Validate a JWT and return its user ID."""

    try:
        # Verify the token signature and expiration
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["sub", "exp"]},
        )

        # Extract and validate the user identifier
        user_id = int(payload["sub"])

        return user_id if user_id > 0 else None

    except (InvalidTokenError, ValueError, TypeError):
        # Reject invalid, expired, or malformed tokens
        return None