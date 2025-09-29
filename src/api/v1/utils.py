import json

from typing import List, Optional

from redis import Redis

from src.schemas import JobResponseSchema


def save_job(redis_client: Redis, job: JobResponseSchema) -> None:
    """Save a job object to Redis.

    :param redis_client: Redis client instance.
    :param job: JobResponseSchema instance to save.
    """
    redis_client.set(f"job:{job.job_id}", json.dumps(job.model_dump(), default=str))


def load_job(redis_client: Redis, job_id: str) -> Optional[JobResponseSchema]:
    """Load a job from Redis by its ID.

    :param redis_client: Redis client instance.
    :param job_id: Unique job identifier (UUID) to load.
    :returns: JobResponseSchema instance if found, otherwise None.
    """
    data = redis_client.get(f"job:{job_id}")
    if not data:
        return None
    return JobResponseSchema(**json.loads(data))


def list_jobs(redis_client: Redis) -> List[JobResponseSchema]:
    """List all jobs stored in Redis.

    :param redis_client: Redis client instance.
    :returns: List of JobResponseSchema objects.
    """
    keys = redis_client.keys("job:*")
    jobs = []
    for key in keys:
        data = redis_client.get(key)
        if data:
            jobs.append(JobResponseSchema(**json.loads(data)))
    return jobs