from types import SimpleNamespace
from unittest.mock import Mock

from app.schemas.answer import GeneratedAnswer
from app.services import dependencies


def test_get_answer_provider_builds_and_caches_provider(
    monkeypatch,
):
    fake_settings = SimpleNamespace(
        answer_model_repo="test/repository",
        answer_model_filename="test-model.gguf",
        answer_context_size=2048,
        answer_gpu_layers=-1,
        answer_max_tokens=256,
    )

    settings_factory = Mock(
        return_value=fake_settings,
    )

    llama_model = Mock()
    outlines_model = Mock()
    generator = Mock()
    provider = Mock()

    llama_factory = Mock()
    llama_factory.from_pretrained.return_value = llama_model

    from_llamacpp = Mock(
        return_value=outlines_model,
    )
    generator_factory = Mock(
        return_value=generator,
    )
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
        "Llama",
        llama_factory,
    )
    monkeypatch.setattr(
        dependencies.outlines,
        "from_llamacpp",
        from_llamacpp,
    )
    monkeypatch.setattr(
        dependencies.outlines,
        "Generator",
        generator_factory,
    )
    monkeypatch.setattr(
        dependencies,
        "OutlinesAnswerProvider",
        provider_factory,
    )

    dependencies.get_answer_provider.cache_clear()

    try:
        first_provider = dependencies.get_answer_provider()
        second_provider = dependencies.get_answer_provider()

        assert first_provider is provider
        assert second_provider is provider
        assert first_provider is second_provider

        settings_factory.assert_called_once_with()

        llama_factory.from_pretrained.assert_called_once_with(
            repo_id="test/repository",
            filename="test-model.gguf",
            n_ctx=2048,
            n_gpu_layers=-1,
            verbose=False,
        )

        from_llamacpp.assert_called_once_with(
            llama_model,
        )

        generator_factory.assert_called_once_with(
            outlines_model,
            GeneratedAnswer,
        )

        provider_factory.assert_called_once_with(
            generator,
            max_tokens=256,
        )
    finally:
        dependencies.get_answer_provider.cache_clear()