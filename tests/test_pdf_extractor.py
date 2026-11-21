from io import BytesIO
from unittest.mock import Mock

import pytest
from pypdf import PdfWriter

from app.services import pdf_extractor
from app.services.pdf_extractor import (
    PdfExtractionError,
    extract_pdf_text,
)


def test_extract_pdf_text_rejects_invalid_pdf():
    stream = BytesIO(b"this is not a PDF")

    with pytest.raises(
        PdfExtractionError,
        match="Invalid PDF file",
    ):
        extract_pdf_text(stream)


def test_extract_pdf_text_rejects_pdf_without_text():
    stream = BytesIO()

    writer = PdfWriter()
    writer.add_blank_page(
        width=100,
        height=100,
    )
    writer.write(stream)
    stream.seek(0)

    with pytest.raises(
        PdfExtractionError,
        match="PDF contains no extractable text",
    ):
        extract_pdf_text(stream)


def test_extract_pdf_text_rejects_encrypted_pdf():
    stream = BytesIO()

    writer = PdfWriter()
    writer.add_blank_page(
        width=100,
        height=100,
    )
    writer.encrypt("secret")
    writer.write(stream)
    stream.seek(0)

    with pytest.raises(
        PdfExtractionError,
        match="Encrypted PDFs are not supported",
    ):
        extract_pdf_text(stream)


def test_extract_pdf_text_joins_nonempty_pages(
    monkeypatch,
):
    first_page = Mock()
    first_page.extract_text.return_value = "  First page  "

    empty_page = Mock()
    empty_page.extract_text.return_value = None

    second_page = Mock()
    second_page.extract_text.return_value = "Second page"

    reader = Mock()
    reader.is_encrypted = False
    reader.pages = [
        first_page,
        empty_page,
        second_page,
    ]

    monkeypatch.setattr(
        pdf_extractor,
        "PdfReader",
        Mock(return_value=reader),
    )

    text = pdf_extractor.extract_pdf_text(
        BytesIO(b"fake PDF contents"),
    )

    assert text == "First page\n\nSecond page"