"""Hand a paper to the worker, or run it in-process when pipeline.eager is set."""

from __future__ import annotations

import logging
import queue
import threading

from app.config import Settings
from app.llm import get_llm_client
from app.pipeline.runner import STAGES, process_paper

log = logging.getLogger("paperlens.pipeline")


# In-process mode runs papers one at a time, in upload order, like the Celery worker
# (--concurrency=1): several papers at once would only fight over the free-tier rate limit.
_queue: queue.Queue[tuple[str, tuple[str, ...]]] = queue.Queue()
_worker: threading.Thread | None = None
_worker_lock = threading.Lock()


def _work() -> None:
    while True:
        paper_id, stages = _queue.get()
        try:
            process_paper(paper_id, llm=get_llm_client, stages=stages)
        except Exception:  # process_paper records its own failures; never kill the worker
            log.exception("in-process worker: %s crashed", paper_id)
        finally:
            _queue.task_done()


def _run_in_thread(paper_id: str, stages: tuple[str, ...]) -> None:
    global _worker
    with _worker_lock:
        if _worker is None or not _worker.is_alive():
            _worker = threading.Thread(target=_work, name="paperlens-pipeline", daemon=True)
            _worker.start()
    _queue.put((paper_id, stages))


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
