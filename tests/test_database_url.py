from sqlalchemy import URL

from app.core.config import Settings
from app.db.session import build_database_url


def test_build_database_url_from_settings():
    settings = Settings(
        postgres_user="fake_user",
        postgres_password="p@ssw0rd/123",
        postgres_host="fake_host",
        postgres_port="5013",
        postgres_db="fake_db",
    )
    url = build_database_url(settings)

    assert isinstance(url, URL)
    assert url.drivername == "postgresql+psycopg"
    assert url.username == "fake_user"
    assert url.password == "p@ssw0rd/123"
    assert url.host == "fake_host"
    assert url.port == 5013
    assert url.database == "fake_db"


def test_rendered_database_url_masks_password():
    fake_password = "p@ssw0rd/123"

    settings = Settings(
        postgres_user="fake_user",
        postgres_password=fake_password,
        postgres_host="fake_host",
        postgres_port="5013",
        postgres_db="fake_db",
    )

    url = build_database_url(settings)
    rendered_url = url.render_as_string()

    assert fake_password not in rendered_url
    assert "***" in rendered_url
