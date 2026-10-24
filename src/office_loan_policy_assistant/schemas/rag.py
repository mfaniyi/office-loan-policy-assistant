from pydantic import BaseModel, Field


class PolicyQuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


class PolicySource(BaseModel):
    document: str
    page_number: int


class PolicyAnswerResponse(BaseModel):
    question: str
    answer: str
    sources: list[PolicySource]
    sources_are_retrieved_context: bool = True
    is_answer_supported: bool | None = None


class EvidenceValidationResult(BaseModel):
    """Represent the result of checking answer support."""

    is_supported: bool
    explanation: str


class AnswerabilityResult(BaseModel):
    """Represent whether policy evidence can answer a question."""

    is_answerable: bool
    explanation: str