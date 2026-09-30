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
    )

    assert settings.postgres_user == "test_user"
    assert settings.postgres_db == "test_database"
    assert settings.postgres_host == "test_host"
    assert settings.postgres_port == 5433


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
