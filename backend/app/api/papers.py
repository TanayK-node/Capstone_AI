"""Papers API (SCOPE.md §7): upload / link, library, status, PDF, parsed blocks, extraction,
progress events (SSE), exports, rerun."""

from __future__ import annotations

import asyncio
import json
import re
import time
from collections.abc import AsyncIterator, Iterator
from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, Response, StreamingResponse
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_sessionmaker
from app.models import (
    BlockRow,
    ClaimReportRow,
    CodeReportRow,
    ExtractionRow,
    MathReportRow,
    Paper,
    ParseResult,
    ReproReport,
)
from app.pipeline import dispatch, export
from app.pipeline.chat.service import answer as chat_answer
from app.pipeline.ingest import storage
from app.pipeline.ingest.resolver import InputError
from app.pipeline.ingest.service import IngestResult, ingest_link, ingest_pdf_bytes
from app.pipeline.ingest.sources import FetchError, NoOpenAccessPdfError
from app.pipeline.ingest.validate import InvalidPdfError
from app.pipeline.results.builder import build_results
from app.pipeline.retrieval.embedder import get_embedder
from app.pipeline.retrieval.store import load_index
from app.pipeline.runner import ANALYSIS_STAGES, STAGES, load_document, stage_statuses
from app.schemas.chat import ChatAnswer, ChatRequest
from app.schemas.extraction import PaperExtraction
from app.schemas.repro import Scorecard
from app.schemas.results import ResultsTable

router = APIRouter(prefix="/api/papers", tags=["papers"])

FINAL_STATUSES = {"ready", "partial", "failed"}
EVENT_POLL_SECONDS = 0.5
EVENT_TIMEOUT_SECONDS = 15 * 60


def get_session() -> Iterator[Session]:
    with get_sessionmaker()() as session:
        yield session


# ------------------------------------------------------------------ response models


class CreatePaperResponse(BaseModel):
    paper_id: str
    status: str
    duplicate: bool
    dispatched_to: str | None


class PaperSummary(BaseModel):
    id: str
    title: str | None
    source_type: str
    source_id: str | None
    status: str
    page_count: int
    created_at: datetime


class PaperDetail(PaperSummary):
    source_url: str | None
    error: str | None
    metadata: dict[str, Any]
    stages: dict[str, dict[str, Any]]
    parse: dict[str, Any] | None


class BlockOut(BaseModel):
    id: str
    type: str
    order: int
    page: int
    bbox: dict[str, Any] | None
    boxes: list[dict[str, Any]]
    section_path: list[str]
    role: str | None
    label: str | None
    text: str
    table: dict[str, Any] | None


class BlocksResponse(BaseModel):
    pages: list[dict[str, Any]]
    blocks: list[BlockOut]


class ExtractionResponse(BaseModel):
    paper_id: str
    verified: bool
    grounding_score: float | None
    provider: str | None
    model: str | None
    prompt_version: str | None
    created_at: datetime
    status_counts: dict[str, int]  # grounding status -> number of evidence quotes
    data: dict[str, Any]  # PaperExtraction


StageName = Literal[
    "parse", "structure", "index", "extract", "verify", "repro", "claims", "code", "math"
]


class RerunRequest(BaseModel):
    stages: list[StageName] | None = None


class ConfirmRepoRequest(BaseModel):
    url: str


# ------------------------------------------------------------------ helpers


def _paper_or_404(session: Session, paper_id: str) -> Paper:
    paper = session.get(Paper, paper_id)
    if paper is None:
        raise HTTPException(404, "paper not found")
    return paper


def _summary(p: Paper) -> PaperSummary:
    return PaperSummary(
        id=p.id,
        title=p.title,
        source_type=p.source_type,
        source_id=p.source_id,
        status=p.status,
        page_count=p.page_count,
        created_at=p.created_at,
    )


# ------------------------------------------------------------------ endpoints


@router.post("", response_model=CreatePaperResponse)
async def create_paper(
    file: UploadFile | None = File(None),
    url: str | None = Form(None),
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> CreatePaperResponse:
    """Multipart form with either `file` (a PDF) or `url` (arXiv id/URL, DOI, PDF link...)."""
    if (file is None) == (not url):
        raise HTTPException(422, "send exactly one of `file` or `url`")
    try:
        if file is not None:
            data = await file.read(settings.ingest.max_mb * 1024 * 1024 + 1)
            result: IngestResult = await run_in_threadpool(
                ingest_pdf_bytes, session, settings, data, source_url=None
            )
        else:
            assert url is not None
            result = await run_in_threadpool(ingest_link, session, settings, url)
    except (InputError, InvalidPdfError) as exc:
        raise HTTPException(422, str(exc)) from exc
    except NoOpenAccessPdfError as exc:
        raise HTTPException(404, str(exc)) from exc
    except FetchError as exc:
        raise HTTPException(502, str(exc)) from exc

    paper = result.paper
    dispatched: str | None = None
    # New papers, and old ones whose processing failed, go (back) into the pipeline. A
    # "partial" paper parsed fine, so only its analysis stages are retried (e.g. once a key is set).
    if result.created or paper.status in ("failed", "partial"):
        stages = ANALYSIS_STAGES if paper.status == "partial" else STAGES
        paper.status = "queued"
        session.commit()
        dispatched = dispatch.enqueue(settings, paper.id, stages)
    return CreatePaperResponse(
        paper_id=paper.id,
        status=paper.status,
        duplicate=not result.created,
        dispatched_to=dispatched,
    )


@router.get("", response_model=list[PaperSummary])
def list_papers(session: Session = Depends(get_session)) -> list[PaperSummary]:
    papers = session.scalars(select(Paper).order_by(Paper.created_at.desc())).all()
    return [_summary(p) for p in papers]


@router.get("/{paper_id}", response_model=PaperDetail)
def get_paper(paper_id: str, session: Session = Depends(get_session)) -> PaperDetail:
    paper = _paper_or_404(session, paper_id)
    parse = session.get(ParseResult, paper_id)
    parse_info: dict[str, Any] | None = None
    if parse is not None:
        counts = dict(
            session.execute(
                select(BlockRow.type, func.count())
                .where(BlockRow.paper_id == paper_id)
                .group_by(BlockRow.type)
            ).all()
        )
        parse_info = {
            "parser": parse.parser,
            "parser_version": parse.parser_version,
            "warnings": parse.warnings,
            "metadata": parse.doc_metadata,
            "sections": parse.sections,
            "block_counts": counts,
            "reference_count": len(parse.references),
        }
    return PaperDetail(
        **_summary(paper).model_dump(),
        source_url=paper.source_url,
        error=paper.error,
        metadata=paper.meta or {},
        stages=stage_statuses(session, paper_id),
        parse=parse_info,
    )


@router.get("/{paper_id}/pdf")
def get_pdf(
    paper_id: str,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    _paper_or_404(session, paper_id)
    path = storage.pdf_path(settings, paper_id)
    if not path.exists():
        raise HTTPException(404, "PDF file missing from storage")
    return FileResponse(path, media_type="application/pdf", filename=f"{paper_id[:12]}.pdf")


@router.get("/{paper_id}/blocks", response_model=BlocksResponse)
def get_blocks(paper_id: str, session: Session = Depends(get_session)) -> BlocksResponse:
    _paper_or_404(session, paper_id)
    parse = session.get(ParseResult, paper_id)
    rows = session.scalars(
        select(BlockRow).where(BlockRow.paper_id == paper_id).order_by(BlockRow.order)
    ).all()
    return BlocksResponse(
        pages=parse.pages if parse else [],
        blocks=[
            BlockOut(
                id=r.id,
                type=r.type,
                order=r.order,
                page=r.page,
                bbox=r.bbox,
                boxes=r.boxes,
                section_path=r.section_path,
                role=r.role,
                label=r.label,
                text=r.text,
                table=(r.data or {}).get("table"),
            )
            for r in rows
        ],
    )


@router.post("/{paper_id}/rerun", response_model=CreatePaperResponse)
def rerun(
    paper_id: str,
    body: RerunRequest | None = None,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> CreatePaperResponse:
    paper = _paper_or_404(session, paper_id)
    stages = tuple(body.stages) if body and body.stages else STAGES
    paper.status = "queued"
    session.commit()
    return CreatePaperResponse(
        paper_id=paper.id,
        status=paper.status,
        duplicate=True,
        dispatched_to=dispatch.enqueue(settings, paper.id, stages),
    )


def _load_extraction(session: Session, paper_id: str) -> ExtractionRow:
    _paper_or_404(session, paper_id)
    row = session.get(ExtractionRow, paper_id)
    if row is None:
        raise HTTPException(404, "no extraction yet for this paper")
    return row


@router.get("/{paper_id}/extraction", response_model=ExtractionResponse)
def get_extraction(paper_id: str, session: Session = Depends(get_session)) -> ExtractionResponse:
    row = _load_extraction(session, paper_id)
    extraction = PaperExtraction.model_validate(row.data)
    counts: dict[str, int] = {}
    for _, item in extraction.all_items():
        for ev in item.evidence:
            counts[ev.grounding_status] = counts.get(ev.grounding_status, 0) + 1
    return ExtractionResponse(
        paper_id=paper_id,
        verified=row.verified,
        grounding_score=row.grounding_score,
        provider=row.provider,
        model=row.model,
        prompt_version=row.prompt_version,
        created_at=row.created_at,
        status_counts=counts,
        data=extraction.model_dump(mode="json"),
    )


@router.get("/{paper_id}/export")
def export_paper(
    paper_id: str,
    format: Literal["json", "md", "bib", "csv"] = Query("json"),
    session: Session = Depends(get_session),
) -> Response:
    row = _load_extraction(session, paper_id)
    media_type, ext = export.FORMATS[format]
    repro = session.get(ReproReport, paper_id)
    card = Scorecard.model_validate(repro.data) if repro is not None else None
    body = export.render(PaperExtraction.model_validate(row.data), format, card)
    name = f"paperlens-{paper_id[:12]}.{ext}"
    return Response(
        body,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


class ReproResponse(BaseModel):
    paper_id: str
    score: float | None
    checklist_version: int
    provider: str | None
    model: str | None
    prompt_version: str | None
    created_at: datetime
    scorecard: dict[str, Any]  # Scorecard


@router.get("/{paper_id}/reproducibility", response_model=ReproResponse)
def get_reproducibility(paper_id: str, session: Session = Depends(get_session)) -> ReproResponse:
    _paper_or_404(session, paper_id)
    row = session.get(ReproReport, paper_id)
    if row is None:
        raise HTTPException(404, "no reproducibility scorecard yet for this paper")
    return ReproResponse(
        paper_id=paper_id,
        score=row.score,
        checklist_version=row.checklist_version,
        provider=row.provider,
        model=row.model,
        prompt_version=row.prompt_version,
        created_at=row.created_at,
        scorecard=row.data,
    )


@router.get("/{paper_id}/tables", response_model=None)
def get_tables(
    paper_id: str,
    format: Literal["json", "csv"] = Query("json"),
    session: Session = Depends(get_session),
) -> list[ResultsTable] | Response:
    """Results tables (M9), rebuilt from the parse; labelled with the extraction if any."""
    _paper_or_404(session, paper_id)
    doc = load_document(session, paper_id)
    if doc is None:
        raise HTTPException(404, "the paper has not been parsed yet")
    row = session.get(ExtractionRow, paper_id)
    extraction = PaperExtraction.model_validate(row.data) if row is not None else None
    tables = build_results(doc, extraction)
    if format == "json":
        return tables
    return Response(
        export.tables_csv(tables),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="paperlens-{paper_id[:12]}-tables.csv"'
        },
    )


@router.get("/{paper_id}/claims")
def get_claims(paper_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Claim verdicts (M8): each claim, the cells it was checked against, recomputed numbers."""
    _paper_or_404(session, paper_id)
    row = session.get(ClaimReportRow, paper_id)
    if row is None:
        raise HTTPException(404, "no claim report yet for this paper")
    return {
        "paper_id": paper_id,
        "provider": row.provider,
        "model": row.model,
        "prompt_version": row.prompt_version,
        "created_at": row.created_at,
        "report": row.data,
    }


@router.get("/{paper_id}/code")
def get_code(paper_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Paper-code consistency (M7): repository, health card, paper vs code rows."""
    _paper_or_404(session, paper_id)
    row = session.get(CodeReportRow, paper_id)
    if row is None:
        raise HTTPException(404, "no code report yet for this paper")
    return {"paper_id": paper_id, "created_at": row.created_at, "report": row.data}


_REPO_URL = re.compile(
    r"^https://(github\.com|gitlab\.com|bitbucket\.org|huggingface\.co)/[\w.-]+/[\w.-]+(/.*)?$"
)


@router.post("/{paper_id}/code/confirm", response_model=CreatePaperResponse)
def confirm_repo(
    paper_id: str,
    body: ConfirmRepoRequest,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> CreatePaperResponse:
    """The user confirms the suggested repository or gives the right one; re-runs the code
    stage with it (SCOPE.md §7)."""
    paper = _paper_or_404(session, paper_id)
    url = body.url.strip()
    if not _REPO_URL.match(url):
        raise HTTPException(422, "give an https link to a GitHub / GitLab / Bitbucket repository")
    paper.meta = {**(paper.meta or {}), "code_repo": url}
    paper.status = "queued"
    session.commit()
    return CreatePaperResponse(
        paper_id=paper.id,
        status=paper.status,
        duplicate=True,
        dispatched_to=dispatch.enqueue(settings, paper.id, ("code",)),
    )


@router.get("/{paper_id}/glossary")
def get_glossary(paper_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Equations and notation glossary (M10)."""
    _paper_or_404(session, paper_id)
    row = session.get(MathReportRow, paper_id)
    if row is None:
        raise HTTPException(404, "no glossary yet for this paper")
    return {"paper_id": paper_id, "model": row.model, "prompt_version": row.prompt_version,
            "created_at": row.created_at, "report": row.data}  # fmt: skip


@router.post("/{paper_id}/chat", response_model=ChatAnswer)
def chat(
    paper_id: str,
    body: ChatRequest,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> ChatAnswer:
    """Grounded Q&A (M11): the answer cites the paper's passages, or refuses."""
    from app.llm import get_llm_client

    _paper_or_404(session, paper_id)
    llm = get_llm_client()
    if not llm.providers:
        raise HTTPException(503, "no LLM provider configured: set GEMINI_API_KEY in .env")
    embedder = get_embedder(settings)
    index = load_index(session, paper_id, embedder)
    if not index.passages:
        raise HTTPException(409, "the paper has not been parsed yet")
    return chat_answer(body, index, embedder, llm, settings)


def _snapshot(paper_id: str) -> tuple[str, str | None, dict[str, dict[str, Any]]] | None:
    with get_sessionmaker()() as session:
        paper = session.get(Paper, paper_id)
        if paper is None:
            return None
        return paper.status, paper.error, stage_statuses(session, paper_id)


def _sse(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


@router.get("/{paper_id}/events")
async def paper_events(paper_id: str, request: Request) -> StreamingResponse:
    """Server-sent events: one `stage` event per stage status change, then `done` with the
    paper's final status. Polls the database, so it works with Celery workers in another
    process as well as with the in-process pipeline."""
    if await run_in_threadpool(_snapshot, paper_id) is None:
        raise HTTPException(404, "paper not found")

    async def stream() -> AsyncIterator[str]:
        seen: dict[str, str] = {}
        last_status = ""
        deadline = time.monotonic() + EVENT_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            snap = await run_in_threadpool(_snapshot, paper_id)
            if snap is None:
                return
            status, error, stages = snap
            for stage, info in stages.items():
                if seen.get(stage) != info["status"]:
                    seen[stage] = info["status"]
                    yield _sse("stage", {"stage": stage, **info})
            if status != last_status:
                last_status = status
                if status in FINAL_STATUSES:
                    yield _sse("done", {"status": status, "error": error})
                    return
                yield _sse("status", {"status": status})
            if await request.is_disconnected():
                return
            await asyncio.sleep(EVENT_POLL_SECONDS)
        yield _sse("timeout", {"status": last_status})

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
