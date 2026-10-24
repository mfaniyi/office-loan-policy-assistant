from sqlalchemy import select
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer

from office_loan_policy_assistant.models.document_chunk import DocumentChunk


def retrieve_policy_chunks(
    question: str,
    db: Session,
    model: SentenceTransformer,
    limit: int = 3,
) -> list[dict]:
    """Retrieve policy chunks using vector similarity."""

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if limit < 1:
        raise ValueError("Limit must be positive.")

    question_embedding = model.encode(
        question,
        normalize_embeddings=True,
    ).tolist()

    distance = DocumentChunk.embedding.cosine_distance(question_embedding)

    statement = (
        select(DocumentChunk, distance.label("distance"))
        .order_by(distance)
        .limit(limit)
    )

    results = db.execute(statement).all()

    return [
        {
            "id": chunk.id,
            "text": chunk.content,
            "page_number": chunk.page_number,
            "source": chunk.source,
            "similarity_score": round(1 - float(distance_value), 4),
        }
        for chunk, distance_value in results
    ]