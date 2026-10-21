"""Celery tasks. Thin wrappers: the logic lives in app.pipeline so tests can call it directly."""

from __future__ import annotations

from app.llm import get_llm_client
from app.pipeline.runner import STAGES, process_paper
from app.workers.celery_app import celery_app


@celery_app.task(name="paperlens.process_paper")
def process_paper_task(paper_id: str, stages: list[str] | None = None) -> str:
    return process_paper(paper_id, llm=get_llm_client, stages=tuple(stages or STAGES))
