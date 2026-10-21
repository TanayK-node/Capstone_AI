"""Ingest (M1): validate + store a PDF and create (or find) its paper record."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.config import Settings
from app.models import Job, Paper
from app.pipeline.ingest import storage
from app.pipeline.ingest.resolver import resolve
from app.pipeline.ingest.sources import SourceFetcher
from app.pipeline.ingest.validate import validate_pdf


@dataclass
class IngestResult:
    paper: Paper
    created: bool  # False when the same PDF (same sha256) was already in the library


def ingest_pdf_bytes(
    session: Session,
    settings: Settings,
    data: bytes,
    *,
    source_type: str = "upload",
    source_id: str | None = None,
    source_url: str | None = None,
    metadata: dict[str, Any] | None = None,
    latex_source: bytes | None = None,
) -> IngestResult:
    started = datetime.now(UTC)
    info = validate_pdf(data, settings.ingest)  # raises InvalidPdfError
    existing = session.get(Paper, info.sha256)
    if existing is not None:
        # Same bytes = same paper (dedupe). Fill in metadata we didn't have before.
        if metadata:
            existing.meta = {**metadata, **(existing.meta or {})}
            existing.title = existing.title or metadata.get("title")
        session.commit()
        return IngestResult(existing, created=False)

    storage.save_pdf(settings, info.sha256, data)
    meta = dict(metadata or {})
    if latex_source:
        storage.save_latex_source(settings, info.sha256, latex_source)
        meta["latex_source"] = True
    paper = Paper(
        id=info.sha256,
        source_type=source_type,
        source_id=source_id,
        source_url=source_url,
        title=meta.get("title"),
        meta=meta,
        status="queued",
        page_count=info.page_count,
    )
    session.add(paper)
    session.add(
        Job(
            paper_id=paper.id,
            stage="ingest",
            status="done",
            started_at=started,
            finished_at=datetime.now(UTC),
            provider=source_type,
            detail={"pages": info.page_count, "bytes": info.size_bytes, "source_id": source_id},
        )
    )
    session.commit()
    return IngestResult(paper, created=True)


def ingest_link(
    session: Session, settings: Settings, raw: str, fetcher: SourceFetcher | None = None
) -> IngestResult:
    """Resolve an arXiv id / DOI / URL, download the PDF, then ingest it."""
    source = resolve(raw)  # raises InputError
    fetched = (fetcher or SourceFetcher(settings)).fetch(source)  # raises FetchError
    return ingest_pdf_bytes(
        session,
        settings,
        fetched.pdf,
        source_type=fetched.kind,
        source_id=fetched.identifier,
        source_url=source.url or fetched.pdf_url,
        metadata=fetched.metadata,
        latex_source=fetched.latex_source,
    )
