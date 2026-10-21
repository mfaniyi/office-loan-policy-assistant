from office_loan_policy_assistant.core.security import (
    hash_password,
    verify_password,
)
from datetime import datetime, timedelta, timezone
import jwt
from office_loan_policy_assistant.core.config import settings
from office_loan_policy_assistant.core.security import (
    create_access_token,
    decode_access_token,
)


# Test that passwords are securely hashed
def test_password_hashing():
    # Generate a hash from a sample password
    password = "TestPassword123!"
    hashed = hash_password(password)

    # Ensure the original password is not stored
    assert hashed != password

    # Ensure the hash is a non-empty string
    assert isinstance(hashed, str)
    assert len(hashed) > 0


# Test that the correct password is accepted
def test_correct_password():
    # Generate a hash from the correct password
    hashed = hash_password("TestPassword123!")

    # Verify the matching password
    assert verify_password("TestPassword123!", hashed) is True


# Test that an incorrect password is rejected
def test_incorrect_password():
    # Generate a hash from the correct password
    hashed = hash_password("TestPassword123!")

    # Verify that an incorrect password is rejected
    assert verify_password("WrongPassword", hashed) is False


# Test that hashing the same password produces different hashes
def test_unique_password_hashes():
    # Generate two hashes using the same password
    first_hash = hash_password("TestPassword123!")
    second_hash = hash_password("TestPassword123!")

    # Verify that each hash uses a unique random salt
    assert first_hash != second_hash

    # Confirm both hashes still validate the original password
    assert verify_password("TestPassword123!", first_hash)
    assert verify_password("TestPassword123!", second_hash)


# Test that a valid JWT returns the correct user ID
def test_valid_access_token():
    token = create_access_token(user_id=1)

    assert decode_access_token(token) == 1


# Test that an invalid JWT is rejected
def test_invalid_access_token():
    assert decode_access_token("invalid-token") is None


# Test that an expired JWT is rejected
def test_expired_access_token():
    # Create an expiration time in the past
    expired_at = datetime.now(timezone.utc) - timedelta(minutes=1)

    # Generate an already-expired token
    token = jwt.encode(
        {"sub": "1", "exp": expired_at},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    # Confirm the expired token is rejected
    assert decode_access_token(token) is None


# Test that a token without a user ID is rejected
def test_token_without_user_id():
    # Generate a token missing the required subject
    token = jwt.encode(
        {
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    # Confirm the malformed token is rejected
    assert decode_access_token(token) is None


# Test that invalid user identifiers are rejected
def test_invalid_user_id():
    token = create_access_token(user_id=0)

    assert decode_access_token(token) is None