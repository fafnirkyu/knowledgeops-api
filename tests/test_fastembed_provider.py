from unittest.mock import Mock

from app.core.embedding import EMBEDDING_DIMENSIONS
from app.services import fastembed_provider


def test_fastembed_provider_adapts_model_output(
    monkeypatch,
):
    first_vector = Mock()
    first_vector.tolist.return_value = (
        [0.1] * EMBEDDING_DIMENSIONS
    )

    second_vector = Mock()
    second_vector.tolist.return_value = (
        [0.2] * EMBEDDING_DIMENSIONS
    )

    model = Mock()
    model.embed.return_value = [
        first_vector,
        second_vector,
    ]

    model_factory = Mock(
        return_value=model,
    )

    monkeypatch.setattr(
        fastembed_provider,
        "TextEmbedding",
        model_factory,
    )

    provider = fastembed_provider.FastEmbedEmbeddingProvider(
        model_name="test-model",
    )

    model_factory.assert_called_once_with(
        model_name="test-model"
    )

    assert provider.dimensions == EMBEDDING_DIMENSIONS

    embeddings = provider.embed(
        ("Olá", "Hello"),
    )

    model.embed.assert_called_once_with(
        ["Olá", "Hello"]
    )

    assert embeddings == [
        [0.1] * EMBEDDING_DIMENSIONS,
        [0.2] * EMBEDDING_DIMENSIONS,
    ]

    assert all(
        isinstance(embedding, list)
        for embedding in embeddings
    )
