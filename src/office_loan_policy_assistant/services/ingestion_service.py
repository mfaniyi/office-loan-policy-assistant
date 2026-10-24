from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from office_loan_policy_assistant.models.document_chunk import DocumentChunk
from office_loan_policy_assistant.services.document_service import extract_pdf_text
from office_loan_policy_assistant.services.chunking_service import chunk_documents
from office_loan_policy_assistant.services.embedding_service import (
    load_embedding_model,
    generate_embeddings,
)


def ingest_policy_document(
    file_path: str | Path,
    db: Session,
) -> int:
    """Extract, embed, and store policy document chunks."""

    pages = extract_pdf_text(file_path)
    chunks = chunk_documents(pages)

    if not chunks:
        raise ValueError("No text chunks were extracted from the document.")

    model = load_embedding_model()
    embedded_chunks = generate_embeddings(chunks, model)

    if len(embedded_chunks) != len(chunks):
        raise ValueError("Embedding generation was incomplete.")

    source = Path(file_path).name

    # Replace existing chunks for this document
    db.execute(
        delete(DocumentChunk).where(DocumentChunk.source == source)
    )

    for chunk in embedded_chunks:
        db.add(
            DocumentChunk(
                source=chunk["source"],
                page_number=chunk["page_number"],
                content=chunk["text"],
                embedding=chunk["embedding"],
            )
        )

    db.commit()

    return len(embedded_chunks)