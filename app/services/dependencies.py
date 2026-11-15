from functools import lru_cache

from app.core.config import Settings
from app.services.embedding_provider import EmbeddingProvider
from app.services.fastembed_provider import (
    FastEmbedEmbeddingProvider,
)


@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    settings = Settings()

    return FastEmbedEmbeddingProvider(
        model_name=settings.embedding_model,
    )