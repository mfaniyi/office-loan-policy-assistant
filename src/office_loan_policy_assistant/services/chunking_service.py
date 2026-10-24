def chunk_documents(
    pages: list[dict],
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[dict]:
    """Split PDF pages into overlapping text chunks."""

    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid chunk size or overlap.")

    chunks = []
    step = chunk_size - overlap

    for page in pages:
        text = page["text"]

        for start in range(0, len(text), step):
            chunk_text = text[start:start + chunk_size].strip()

            if not chunk_text:
                continue

            chunks.append(
                {
                    "text": chunk_text,
                    "page_number": page["page_number"],
                    "source": page["source"],
                }
            )

    return chunks
