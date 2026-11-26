import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_accepts_explicit_values():
    settings = Settings(
        postgres_user="test_user",
        postgres_password="test_password",
        postgres_db="test_database",
        postgres_host="test_host",
        postgres_port=5433,
        redis_url="redis://test-redis:6379/1",
        redis_queue_name="test-processing",
        answer_model_repo="test/repository",
        answer_model_filename="test-model.gguf",
        answer_context_size=2048,
        answer_max_tokens=256,
        answer_gpu_layers=-1,
    )

    assert settings.postgres_user == "test_user"
    assert settings.postgres_db == "test_database"
    assert settings.postgres_host == "test_host"
    assert settings.postgres_port == 5433

    assert settings.embedding_model == (
        "sentence-transformers/"
        "paraphrase-multilingual-MiniLM-L12-v2"
    )
    assert str(settings.redis_url) == "redis://test-redis:6379/1"
    assert settings.redis_queue_name == "test-processing"
    assert settings.answer_model_repo == "test/repository"
    assert settings.answer_model_filename == "test-model.gguf"
    assert settings.answer_context_size == 2048
    assert settings.answer_max_tokens == 256
    assert settings.answer_gpu_layers == -1


def test_settings_converts_port_string_to_integer():
    settings = Settings(
        postgres_user="test_user",
        postgres_password="test_password",
        postgres_db="test_database",
        postgres_host="test_host",
        postgres_port="5433",
    )

    assert settings.postgres_port == 5433
    assert isinstance(settings.postgres_port, int)


def test_settings_masks_and_retrieves_secret():
    settings = Settings(
        postgres_user="test_user",
        postgres_password="test_password",
        postgres_db="test_database",
        postgres_host="test_host",
        postgres_port="5433",
    )

    assert str(settings.postgres_password) == "**********"
    assert settings.postgres_password.get_secret_value() == "test_password"


def test_settings_rejects_invalid_port():
    with pytest.raises(ValidationError):
        Settings(
            postgres_user="test_user",
            postgres_password="test_password",
            postgres_db="test_database",
            postgres_host="localhost",
            postgres_port="not-a-port",
        )
