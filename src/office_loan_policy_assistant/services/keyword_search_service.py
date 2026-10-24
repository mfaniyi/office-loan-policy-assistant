from sqlalchemy import func, select
from sqlalchemy.orm import Session

from office_loan_policy_assistant.models.document_chunk import DocumentChunk


def keyword_search(
    question: str,
    db: Session,
    limit: int = 5,
) -> list[dict]:
    """Retrieve policy chunks using PostgreSQL full-text search."""

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if limit < 1:
        raise ValueError("Limit must be positive.")

    document_vector = func.to_tsvector(
        "english",
        DocumentChunk.content,
    )

    search_query = func.websearch_to_tsquery(
        "english",
        question,
    )

    rank = func.ts_rank(
        document_vector,
        search_query,
    )

    statement = (
        select(DocumentChunk, rank.label("rank"))
        .where(document_vector.op("@@")(search_query))
        .order_by(rank.desc(), DocumentChunk.id)
        .limit(limit)
    )

    results = db.execute(statement).all()

    return [
        {
            "id": chunk.id,
            "text": chunk.content,
            "page_number": chunk.page_number,
            "source": chunk.source,
            "keyword_score": round(float(score), 4),
        }
        for chunk, score in results
    ]
