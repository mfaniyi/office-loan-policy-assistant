from pathlib import Path

from office_loan_policy_assistant.db.database import SessionLocal
from office_loan_policy_assistant.services.ingestion_service import (
    ingest_policy_document,
)


def main() -> None:
    """Ingest the Office Loan Policy into PostgreSQL."""

    policy_path = Path("documents/loan_policy/office_loan_policy.pdf")

    with SessionLocal() as db:
        count = ingest_policy_document(
            file_path=policy_path,
            db=db,
        )

    print(f"Successfully stored {count} policy chunks.")


if __name__ == "__main__":
    main()