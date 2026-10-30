from sqlalchemy.engine import make_url

from office_loan_policy_assistant.core.config import Settings


def test_database_url_uses_system_certificate_store():
    # Use dummy credentials so this test never requires a real database.
    config = Settings(
        POSTGRES_USER="test_user",
        POSTGRES_PASSWORD="test_password",
        POSTGRES_DB="test_db",
        POSTGRES_HOST="localhost",
        POSTGRES_PORT=5433,
        POSTGRES_SSLMODE="verify-full",
        JWT_SECRET_KEY="test_only_not_a_real_secret",
    )

    # Parse the URL and verify TLS settings without exposing credentials.
    url = make_url(config.database_url)

    assert url.drivername == "postgresql+psycopg"
    assert url.query["sslmode"] == "verify-full"
    assert url.query["sslrootcert"] == "/etc/ssl/certs/ca-certificates.crt"
    assert url.host == "localhost"
    assert url.database == "test_db"
