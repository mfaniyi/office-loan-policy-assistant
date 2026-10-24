from pathlib import Path

import pymupdf


def extract_pdf_text(file_path: str | Path) -> list[dict]:
    """Extract text and page numbers from a PDF document."""

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"PDF not found: {file_path}")

    pages = []

    with pymupdf.open(file_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            if text:
                pages.append(
        {
                        "page_number": page_number,
                        "text": text,
                        "source": file_path.name,
                    }
                )

    return pages