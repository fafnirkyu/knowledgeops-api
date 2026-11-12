from app.services.embedding_provider import EmbeddingProvider


def get_embedding_provider() -> EmbeddingProvider:
    raise RuntimeError(
        "Embedding provider is not configured"
    )