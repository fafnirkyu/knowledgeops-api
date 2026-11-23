from app.core.config import Settings
from app.jobs.queue import (
    create_document_queue,
    get_document_queue,
)


def test_create_document_queue_uses_settings():
    settings = Settings(
        postgres_user="test_user",
        postgres_password="test_password",
        postgres_db="test_database",
        redis_url="redis://test-redis:6380/2",
        redis_queue_name="test-processing",
    )

    queue = create_document_queue(settings)

    connection_options = (
        queue.connection
        .connection_pool
        .connection_kwargs
    )

    assert queue.name == "test-processing"
    assert connection_options["host"] == "test-redis"
    assert connection_options["port"] == 6380
    assert connection_options["db"] == 2


def test_get_document_queue_is_cached():
    get_document_queue.cache_clear()

    try:
        first_queue = get_document_queue()
        second_queue = get_document_queue()

        assert first_queue is second_queue
    finally:
        get_document_queue.cache_clear()