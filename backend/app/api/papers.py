"""Papers API (SCOPE.md §7): upload / link, library, status, PDF, parsed blocks, rerun."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_sessionmaker
from app.models import BlockRow, Paper, ParseResult
from app.pipeline import dispatch
from app.pipeline.ingest import storage
from app.pipeline.ingest.resolver import InputError
from app.pipeline.ingest.service import IngestResult, ingest_link, ingest_pdf_bytes
from app.pipeline.ingest.sources import FetchError, NoOpenAccessPdfError
from app.pipeline.ingest.validate import InvalidPdfError
from app.pipeline.runner import STAGES, stage_statuses

router = APIRouter(prefix="/api/papers", tags=["papers"])


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


class RerunRequest(BaseModel):
    stages: list[Literal["parse", "structure"]] | None = None


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
    # New papers, and old ones whose processing failed, go (back) into the pipeline.
    if result.created or paper.status == "failed":
        paper.status = "queued"
        session.commit()
        dispatched = dispatch.enqueue(settings, paper.id)
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
