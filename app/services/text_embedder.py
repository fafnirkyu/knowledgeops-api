from collections.abc import Sequence

from app.core.embedding import EMBEDDING_DIMENSIONS
from app.services.embedding_provider import EmbeddingProvider


def embed_texts(
    provider: EmbeddingProvider,
    texts: Sequence[str],
) -> list[list[float]]:
    if provider.dimensions != EMBEDDING_DIMENSIONS:
        raise ValueError(
            "provider dimensions must match storage dimensions"
        )

    embeddings = provider.embed(texts)

    if len(embeddings) != len(texts):
        raise ValueError(
            "embedding count must match text count"
        )

    if any(
        len(embedding) != EMBEDDING_DIMENSIONS
        for embedding in embeddings
    ):
        raise ValueError(
            "embedding vector dimensions must match storage dimensions"
        )

    return embeddings