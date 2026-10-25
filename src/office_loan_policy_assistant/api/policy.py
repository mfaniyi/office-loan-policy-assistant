import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from office_loan_policy_assistant.db.database import get_db
from office_loan_policy_assistant.schemas.rag import (
    PolicyAnswerResponse,
    PolicyQuestionRequest,
)
from office_loan_policy_assistant.services.rag_service import (
    answer_policy_question_with_models,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/policy", tags=["Policy"])


@router.post("/ask", response_model=PolicyAnswerResponse)
def ask_policy_question(
    request: PolicyQuestionRequest,
    db: Annotated[Session, Depends(get_db)],
) -> PolicyAnswerResponse:
    """Answer questions using the Office Loan Policy."""

    try:
        return answer_policy_question_with_models(
            question=request.question,
            db=db,
        )

    except Exception:
        logger.exception("Policy question processing failed")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "The policy assistant is temporarily unavailable. "
                "Please try again later."
            ),
        )