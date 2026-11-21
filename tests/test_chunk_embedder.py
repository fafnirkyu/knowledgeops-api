from collections.abc import Sequence

import pytest

from app.core.embedding import EMBEDDING_DIMENSIONS
from app.services.chunk_embedder import embed_chunks
from app.services.text_chunker import chunk_text


class RecordingEmbeddingProvider:
    dimensions = EMBEDDING_DIMENSIONS

    def __init__(self):
        self.received_texts: list[str] = []

    def embed(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        self.received_texts = list(texts)

        return [
            [
                float(len(text)),
            ] + [
                0.0
            ] * (self.dimensions - 1)
            for text in texts
        ]


class MissingEmbeddingProvider(RecordingEmbeddingProvider):
    def embed(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        embeddings = super().embed(texts)
        return embeddings[:-1]


class WrongVectorSizeProvider(RecordingEmbeddingProvider):
    def embed(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        embeddings = super().embed(texts)
        embeddings[0] = embeddings[0][:-1]
        return embeddings


def test_embed_chunks_sends_chunk_content_to_provider():
    chunks = chunk_text(
        "ABCDEFGHIJ",
        chunk_size=4,
        overlap=1,
    )
    provider = RecordingEmbeddingProvider()

    embeddings = embed_chunks(
        provider=provider,
        chunks=chunks,
    )

    assert provider.received_texts == [
        "ABCD",
        "DEFG",
        "GHIJ",
    ]
    assert len(embeddings) == 3
    assert all(
        len(embedding) == provider.dimensions
        for embedding in embeddings
    )


def test_embed_chunks_rejects_provider_with_wrong_dimensions():
    provider = RecordingEmbeddingProvider()
    provider.dimensions = 3

    chunks = chunk_text(
        "ABCD",
        chunk_size=4,
        overlap=1,
    )

    with pytest.raises(
        ValueError,
        match="provider dimensions must match storage dimensions",
    ):
        embed_chunks(
            provider=provider,
            chunks=chunks,
        )


def test_embed_chunks_rejects_wrong_embedding_count():
    provider = MissingEmbeddingProvider()

    chunks = chunk_text(
        "ABCDEFGH",
        chunk_size=4,
        overlap=0,
    )

    with pytest.raises(
        ValueError,
        match="embedding count must match text count",
    ):
        embed_chunks(
            provider=provider,
            chunks=chunks,
        )


def test_embed_chunks_rejects_wrong_vector_size():
    provider = WrongVectorSizeProvider()

    chunks = chunk_text(
        "ABCD",
        chunk_size=4,
        overlap=0,
    )

    with pytest.raises(
        ValueError,
        match="embedding vector dimensions must match storage dimensions",
    ):
        embed_chunks(
            provider=provider,
            chunks=chunks,
        )
