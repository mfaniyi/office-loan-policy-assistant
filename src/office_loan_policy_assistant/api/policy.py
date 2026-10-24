from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from office_loan_policy_assistant.db.database import get_db
from office_loan_policy_assistant.schemas.rag import (
    PolicyAnswerResponse,
    PolicyQuestionRequest,
)
from office_loan_policy_assistant.services.rag_service import (
    answer_policy_question_with_models,
)


router = APIRouter(prefix="/policy", tags=["Policy"])


@router.post("/ask", response_model=PolicyAnswerResponse)
def ask_policy_question(
    request: PolicyQuestionRequest,
    db: Annotated[Session, Depends(get_db)],
) -> PolicyAnswerResponse:
    """Answer questions using the Office Loan Policy."""

    return answer_policy_question_with_models(
        question=request.question,
        db=db,
    )