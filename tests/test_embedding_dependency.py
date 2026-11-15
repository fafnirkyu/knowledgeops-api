from types import SimpleNamespace
from unittest.mock import Mock

from app.services import dependencies


def test_get_embedding_provider_builds_and_caches_provider(
    monkeypatch,
):
    fake_settings = SimpleNamespace(
        embedding_model="test-model",
    )

    settings_factory = Mock(
        return_value=fake_settings,
    )

    provider = Mock()

    provider_factory = Mock(
        return_value=provider,
    )

    monkeypatch.setattr(
        dependencies,
        "Settings",
        settings_factory,
    )

    monkeypatch.setattr(
        dependencies,
        "FastEmbedEmbeddingProvider",
        provider_factory,
    )

    dependencies.get_embedding_provider.cache_clear()

    try:
        first_provider = dependencies.get_embedding_provider()
        second_provider = dependencies.get_embedding_provider()

        assert first_provider is provider
        assert second_provider is provider
        assert first_provider is second_provider

        settings_factory.assert_called_once_with()

        provider_factory.assert_called_once_with(
            model_name="test-model",
        )
    finally:
        dependencies.get_embedding_provider.cache_clear()
