from redis import Redis

from src.core.config import settings


def create_redis_instance(
    host: str = settings.redis.host,
    port: int = settings.redis.port,
    db: int = settings.redis.db,
) -> Redis:
    """Create and return a Redis client instance.

    :param host: Redis server host. Defaults to the value from settings.
    :param port: Redis server port. Defaults to the value from settings.
    :param db: Redis database index. Defaults to the value from settings.
    :returns: Redis client instance connected to the specified host, port, and database.
    """
    return Redis(host=host, port=port, db=db)