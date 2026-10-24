from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer

from office_loan_policy_assistant.services.keyword_search_service import (
    keyword_search,
)
from office_loan_policy_assistant.services.retrieval_service import (
    retrieve_policy_chunks,
)


def hybrid_search(
    question: str,
    db: Session,
    model: SentenceTransformer,
    limit: int = 5,
    candidate_limit: int = 10,
    rrf_k: int = 60,
) -> list[dict]:
    """Combine semantic and keyword search using RRF."""

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if limit < 1 or candidate_limit < 1 or rrf_k <= 0:
        raise ValueError("Invalid search parameters.")

    candidate_limit = max(candidate_limit, limit)

    semantic_results = retrieve_policy_chunks(
        question=question,
        db=db,
        model=model,
        limit=candidate_limit,
    )

    keyword_results = keyword_search(
        question=question,
        db=db,
        limit=candidate_limit,
    )

    combined = {}

    for results in (semantic_results, keyword_results):
        for rank, chunk in enumerate(results, start=1):
            chunk_id = chunk["id"]

            if chunk_id not in combined:
                combined[chunk_id] = {
                    **chunk,
                    "rrf_score": 0.0,
                }

            combined[chunk_id]["rrf_score"] += 1 / (rrf_k + rank)

    ranked_results = sorted(
        combined.values(),
        key=lambda item: (-item["rrf_score"], item["id"]),
    )

    return ranked_results[:limit]