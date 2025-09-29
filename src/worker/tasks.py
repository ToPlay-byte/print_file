import time

from src.utils import create_redis_instance
from src.api.v1.utils import load_job, save_job


from src.core.celery_conf import celery_app

@celery_app.task
def process_job(job_id: str) -> None:
    """Process a print job in stages, updating its status in Redis.

    The workflow:
    1. Load the job from Redis by ID.
    2. Wait for 5 minutes (simulate processing delay).
    3. Update the job status to 'printing' if it hasn't been canceled or errored.
    4. Wait another 5 minutes (simulate printing delay).
    5. Update the job status to 'done' if it hasn't been canceled or errored.

    :param job_id: Unique job identifier (UUID) to process.
    """
    with create_redis_instance() as redis_client:

        job = load_job(redis_client, job_id)

        if job is None:
            return None

        time.sleep(300)

        job = load_job(redis_client, job_id)

        if job.status in ["canceled", "error"]:
            return None

        job.status = 'printing'

        save_job(redis_client, job)

        time.sleep(300)

        if job.status in ["canceled", "error"]:
            return None

        job.status = "done"

        save_job(redis_client, job)
