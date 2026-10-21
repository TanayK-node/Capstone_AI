"""Celery app. Pipeline stage tasks get registered here from Phase 1 on."""

from __future__ import annotations

from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery("paperlens", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_acks_late=True,  # a crashed worker's stage is re-run, stages are idempotent
    worker_prefetch_multiplier=1,
)


@celery_app.task(name="paperlens.ping")
def ping() -> str:
    return "pong"
