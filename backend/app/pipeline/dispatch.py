"""Hand a paper to the worker, or run it in-process when pipeline.eager is set."""

from __future__ import annotations

import logging
import threading

from app.config import Settings
from app.llm import get_llm_client
from app.pipeline.runner import STAGES, process_paper

log = logging.getLogger("paperlens.pipeline")


def _run_in_thread(paper_id: str, stages: tuple[str, ...]) -> None:
    threading.Thread(
        target=process_paper,
        args=(paper_id,),
        kwargs={"llm": get_llm_client, "stages": stages},
        daemon=True,
    ).start()


def enqueue(settings: Settings, paper_id: str, stages: tuple[str, ...] = STAGES) -> str:
    """Returns "celery" or "thread" (where the work went)."""
    if settings.pipeline.eager:
        _run_in_thread(paper_id, stages)
        return "thread"
    from app.workers.tasks import process_paper_task

    try:
        # retry=False: fail fast if the broker is down instead of blocking the request.
        process_paper_task.apply_async(args=(paper_id, list(stages)), retry=False)
        return "celery"
    except Exception as exc:  # broker down: keep the app usable, but say so in the logs
        log.warning("celery unavailable (%s); running %s in-process", exc, paper_id)
        _run_in_thread(paper_id, stages)
        return "thread"
