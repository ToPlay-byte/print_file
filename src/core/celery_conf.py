from celery import Celery

from src.core.config import settings


def create_celery_app() -> Celery:
    """Create Celery app."""

    app = Celery(
        "celery",
        broker=settings.celery.broker,
        backend=settings.celery.backend,
        include=["src.worker"]
    )
    app.conf.update(
        task_serializer=settings.celery.task_serializer,
        result_serializer=settings.celery.result_serializer,
        accept_content=["json"],
        timezone="UTC",
    )

    return app


celery_app = create_celery_app()
