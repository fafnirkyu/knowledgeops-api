import pytest

from app.services.text_chunker import chunk_text


def test_chunk_text_creates_overlapping_chunks():
    text = "ABCDEFGHIJ"

    chunks = chunk_text(
        text,
        chunk_size=4,
        overlap=1,
    )

    content = [chunk.content for chunk in chunks]

    assert len(chunks) == 3
    assert content == [
        "ABCD",
        "DEFG",
        "GHIJ",
    ]
    assert [chunk.chunk_index for chunk in chunks] == [
        0,
        1,
        2,
    ]

    for chunk in chunks:
        assert (
            text[chunk.start_offset:chunk.end_offset]
            == chunk.content
        )


def test_chunk_text_returns_empty_list_for_empty_text():
    text = ""
    chunks = chunk_text(text)

    assert chunks == []


@pytest.mark.parametrize(
    ("chunk_size", "overlap"),
    [
        (0, 0),  # zero-sized chunks
        (3, -1),  # negative overlap
        (3, 3),  # overlap equals chunk size
    ],
)
def test_chunk_text_rejects_invalid_settings(
    chunk_size: int,
    overlap: int,
):
    with pytest.raises(ValueError):
        chunk_text(
            "Some text",
            chunk_size=chunk_size,
            overlap=overlap,
        )