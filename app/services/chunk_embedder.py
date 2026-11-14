from collections.abc import Sequence

from app.services.embedding_provider import EmbeddingProvider
from app.services.text_chunker import TextChunk
from app.services.text_embedder import embed_texts


def embed_chunks(
    provider: EmbeddingProvider,
    chunks: Sequence[TextChunk],
) -> list[list[float]]:
    texts = [
        chunk.content
        for chunk in chunks
    ]

    return embed_texts(
        provider=provider,
        texts=texts,
    )