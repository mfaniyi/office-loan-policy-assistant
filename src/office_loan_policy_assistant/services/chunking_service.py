def chunk_documents(
    pages: list[dict],
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[dict]:
    """Split PDF pages into overlapping paragraph-aware chunks."""

    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid chunk size or overlap.")

    chunks = []

    for page in pages:
        text = page["text"].strip()

        if not text:
            continue

        paragraphs = [
            paragraph.strip()
            for paragraph in text.split("\n\n")
            if paragraph.strip()
        ]

        current_chunk = ""

        for paragraph in paragraphs:
            if len(paragraph) > chunk_size:
                if current_chunk:
                    chunks.append({
                        "text": current_chunk,
                        "page_number": page["page_number"],
                        "source": page["source"],
                    })
                    current_chunk = ""

                words = paragraph.split()
                word_chunk = ""


                for word in words:
                    candidate = f"{word_chunk} {word}".strip()

                    if len(candidate) > chunk_size and word_chunk:
                        chunks.append({
                            "text": word_chunk,
                            "page_number": page["page_number"],
                            "source": page["source"],
                        })
                        word_chunk = word
                    else:
                        word_chunk = candidate

                if word_chunk:
                    current_chunk = word_chunk

                continue

            candidate = f"{current_chunk}\n\n{paragraph}".strip()

            if len(candidate) > chunk_size and current_chunk:
                chunks.append({
                    "text": current_chunk,
                    "page_number": page["page_number"],
                    "source": page["source"],
                })

                current_chunk = paragraph
            else:
                current_chunk = candidate

        if current_chunk:
            chunks.append({
                "text": current_chunk,
                "page_number": page["page_number"],
                "source": page["source"],
            })

    original_texts = [chunk["text"] for chunk in chunks]

    if overlap > 0:
        for index in range(1, len(chunks)):
            previous = chunks[index - 1]
            current = chunks[index]

            if previous["page_number"] != current["page_number"]:
                continue

            previous_words = original_texts[index - 1].split()
            overlap_words = []
            overlap_length = 0

            for word in reversed(previous_words):
                if overlap_length + len(word) + 1 > overlap:
                    break

                overlap_words.insert(0, word)
                overlap_length += len(word) + 1

            overlap_text = " ".join(overlap_words)

            if overlap_text:
                current["text"] = (
                    overlap_text + " " + current["text"]
                )

    return chunks