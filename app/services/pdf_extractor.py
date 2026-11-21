from typing import BinaryIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError


class PdfExtractionError(ValueError):
    pass


def extract_pdf_text(stream: BinaryIO) -> str:
    try:
        reader = PdfReader(stream)

        if reader.is_encrypted:
            raise PdfExtractionError(
                "Encrypted PDFs are not supported"
            )

        page_texts = [
            (page.extract_text() or "").strip()
            for page in reader.pages
        ]

    except PdfReadError as error:
        raise PdfExtractionError(
            "Invalid PDF file"
        ) from error

    text = "\n\n".join(
        page_text
        for page_text in page_texts
        if page_text
    )

    if not text:
        raise PdfExtractionError(
            "PDF contains no extractable text"
        )

    return text