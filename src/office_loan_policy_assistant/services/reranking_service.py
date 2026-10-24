from sentence_transformers import CrossEncoder


RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def load_reranker() -> CrossEncoder:
    """Load the cross-encoder reranking model."""

    return CrossEncoder(RERANKER_MODEL)


def rerank_chunks(
    question: str,
    chunks: list[dict],
    model: CrossEncoder,
    limit: int = 3,
) -> list[dict]:
    """Rerank retrieved policy chunks by relevance."""

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if limit < 1:
        raise ValueError("Limit must be positive.")

    if not chunks:
        return []

    pairs = [
        (question, chunk["text"])
        for chunk in chunks
    ]

    scores = model.predict(pairs)

    ranked = [
        {
            **chunk,
            "rerank_score": float(score),
        }
        for chunk, score in zip(chunks, scores)
    ]

    ranked = [
        {
            **chunk,
            "rerank_score": float(score),
        }
        for chunk, score in zip(chunks, scores)
    ]

    ranked.sort(
        key=lambda item: item["rerank_score"],
        reverse=True,
    )

    return ranked[:limit]