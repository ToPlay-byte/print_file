from typing import Generator

from redis import Redis

from src.utils import create_redis_instance



def get_redis() -> Redis:
    client = create_redis_instance()
    try:
        yield client
    finally:
        client.close()