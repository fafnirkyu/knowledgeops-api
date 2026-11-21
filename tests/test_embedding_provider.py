from collections.abc import Sequence

from app.services.embedding_provider import EmbeddingProvider


class FakeEmbeddingProvider:
    dimensions = 3

    def embed(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        embeddings = []

        for text in texts:
            embeddings.append(
                [
                    float(len(text)),
                    0.0,
                    1.0,
                ]
            )

        return embeddings


def test_fake_provider_returns_one_vector_per_text():
    provider: EmbeddingProvider = FakeEmbeddingProvider()

    embeddings = provider.embed(
        [
            "cat",
            "database",
        ]
    )

    assert provider.dimensions == 3
    assert len(embeddings) == 2
    assert embeddings[0] == [3.0, 0.0, 1.0]
    assert embeddings[1] == [8.0, 0.0, 1.0]
