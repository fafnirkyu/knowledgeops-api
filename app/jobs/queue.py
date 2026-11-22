from functools import lru_cache

from redis import Redis
from rq import Queue

from app.core.config import Settings


def create_document_queue(
    settings: Settings,
) -> Queue:
    connection = Redis.from_url(
        str(settings.redis_url)
    )

    return Queue(
        name=settings.redis_queue_name,
        connection=connection,
    )


@lru_cache(maxsize=1)
def get_document_queue() -> Queue:
    return create_document_queue(
        Settings()
    )