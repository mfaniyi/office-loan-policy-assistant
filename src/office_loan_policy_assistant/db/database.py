from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from office_loan_policy_assistant.core.config import settings


# Create the PostgreSQL database engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)


# Configure database sessions
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


# Define the base class for our database models
class Base(DeclarativeBase):
    pass


# Provide a database session to API endpoints
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()