from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_embedding_model() -> SentenceTransformer:
    """Load the embedding model."""
    return SentenceTransformer(MODEL_NAME)


def generate_embeddings(
    chunks: list[dict],
    model: SentenceTransformer,
) -> list[dict]:
    """Generate embeddings whilechunk metadata."""

    if not chunks:
        return []

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
    )

    return [
        {
            **chunk,
            "embedding": embedding.tolist(),
        }
        for chunk, embedding in zip(chunks, embeddings)
    ]