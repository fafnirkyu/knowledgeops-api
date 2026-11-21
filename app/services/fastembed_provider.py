from collections.abc import Sequence

from fastembed import TextEmbedding

from app.core.embedding import EMBEDDING_DIMENSIONS


class FastEmbedEmbeddingProvider:
    dimensions = EMBEDDING_DIMENSIONS

    def __init__(self, model_name: str):
        self._model = TextEmbedding(
            model_name=model_name,
        )

    def embed(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        generated_embeddings = self._model.embed(
            list(texts),
        )

        return [
            embedding.tolist()
            for embedding in generated_embeddings
        ]
