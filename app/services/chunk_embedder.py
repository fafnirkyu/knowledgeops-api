from collections.abc import Sequence

from app.core.embedding import EMBEDDING_DIMENSIONS
from app.services.embedding_provider import EmbeddingProvider
from app.services.text_chunker import TextChunk


def embed_chunks(
    provider: EmbeddingProvider,
    chunks: Sequence[TextChunk],
) -> list[list[float]]:
    if provider.dimensions != EMBEDDING_DIMENSIONS:
        raise ValueError(
            "provider dimensions must match storage dimensions"
        )

    texts = [
        chunk.content
        for chunk in chunks
    ]

    embeddings = provider.embed(texts)

    if len(embeddings) != len(chunks):
        raise ValueError(
            "embedding count must match chunk count"
        )

    if any(
        len(embedding) != EMBEDDING_DIMENSIONS
        for embedding in embeddings
    ):
        raise ValueError(
            "embedding vector dimensions must match storage dimensions"
        )

    return embeddings