"""Stage runner: Parse -> Structure for one paper (Phase 1 stages).

Every stage is idempotent (CLAUDE.md rule 8): it deletes its previous output for the paper
before writing, and records a Job row with what produced the result.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings, get_settings
from app.llm.client import LLMClient
from app.models import BlockRow, ChunkRow, Job, Paper, ParseResult
from app.pipeline.ingest import storage
from app.pipeline.parse import get_parser
from app.pipeline.structure.sections import structure_document
from app.schemas.document import (
    Block,
    DocumentMetadata,
    PageInfo,
    ParsedDocument,
    Reference,
    Sentence,
    TableData,
)

log = logging.getLogger("paperlens.pipeline")

STAGES = ("parse", "structure")


@contextmanager
def stage_job(session: Session, paper_id: str, stage: str) -> Iterator[Job]:
    job = Job(paper_id=paper_id, stage=stage, status="running", started_at=datetime.now(UTC))
    session.add(job)
    session.commit()
    try:
        yield job
        job.status = "done"
    except Exception as exc:
        session.rollback()
        job = session.merge(job)
        job.status = "failed"
        job.error = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        job.finished_at = datetime.now(UTC)
        session.commit()


# ------------------------------------------------------------------ persistence


def save_document(session: Session, paper: Paper, doc: ParsedDocument) -> None:
    session.execute(delete(BlockRow).where(BlockRow.paper_id == paper.id))
    session.execute(delete(ChunkRow).where(ChunkRow.paper_id == paper.id))
    session.execute(delete(ParseResult).where(ParseResult.paper_id == paper.id))
    session.add_all(
        BlockRow(
            paper_id=paper.id,
            id=b.id,
            type=b.type,
            order=b.order,
            page=b.page,
            bbox=b.bbox.model_dump() if b.bbox else None,
            boxes=[x.model_dump() for x in b.boxes],
            section_path=b.section_path,
            label=b.label,
            text=b.text,
            data={
                "sentences": [s.model_dump() for s in b.sentences],
                "table": b.table.model_dump() if b.table else None,
            },
        )
        for b in doc.blocks
    )
    session.add(
        ParseResult(
            paper_id=paper.id,
            parser=doc.parser,
            parser_version=doc.parser_version,
            pages=[p.model_dump() for p in doc.pages],
            doc_metadata=doc.metadata.model_dump(),
            references=[r.model_dump() for r in doc.references],
            warnings=doc.warnings,
            sections=[],
        )
    )


def load_document(session: Session, paper_id: str) -> ParsedDocument | None:
    result = session.get(ParseResult, paper_id)
    if result is None:
        return None
    rows = session.scalars(
        select(BlockRow).where(BlockRow.paper_id == paper_id).order_by(BlockRow.order)
    ).all()
    blocks = [
        Block(
            id=r.id,
            type=r.type,
            order=r.order,
            page=r.page,
            bbox=r.bbox,
            boxes=r.boxes,
            section_path=r.section_path,
            text=r.text,
            label=r.label,
            sentences=[Sentence.model_validate(s) for s in (r.data or {}).get("sentences", [])],
            table=TableData.model_validate(t) if (t := (r.data or {}).get("table")) else None,
        )
        for r in rows
    ]
    return ParsedDocument(
        parser=result.parser,
        parser_version=result.parser_version,
        pages=[PageInfo.model_validate(p) for p in result.pages],
        metadata=DocumentMetadata.model_validate(result.doc_metadata),
        blocks=blocks,
        references=[Reference.model_validate(r) for r in result.references],
        warnings=result.warnings,
    )


# ------------------------------------------------------------------ stages


def run_parse(session: Session, settings: Settings, paper: Paper) -> ParsedDocument:
    with stage_job(session, paper.id, "parse") as job:
        parser = get_parser(settings)
        doc = parser.parse(storage.pdf_path(settings, paper.id))
        save_document(session, paper, doc)
        if not paper.title and doc.metadata.title:
            paper.title = doc.metadata.title
        job.provider, job.model = doc.parser, doc.parser_version
        job.detail = {
            "blocks": len(doc.blocks),
            "tables": len(doc.tables),
            "references": len(doc.references),
            "warnings": doc.warnings,
        }
    return doc


def run_structure(
    session: Session, paper: Paper, doc: ParsedDocument, llm: LLMClient | None
) -> None:
    with stage_job(session, paper.id, "structure") as job:
        result = structure_document(doc, llm)
        session.execute(delete(ChunkRow).where(ChunkRow.paper_id == paper.id))
        for row in session.scalars(select(BlockRow).where(BlockRow.paper_id == paper.id)):
            row.role = result.block_roles.get(row.id)
        session.add_all(
            ChunkRow(
                paper_id=paper.id,
                id=c.id,
                level=c.level,
                parent_id=c.parent_id,
                order=c.order,
                block_ids=c.block_ids,
                section_path=c.section_path,
                role=c.role,
                page=c.page,
                boxes=[b.model_dump() for b in c.boxes],
                text=c.text,
            )
            for c in result.chunks
        )
        parse_result = session.get(ParseResult, paper.id)
        if parse_result is not None:
            parse_result.sections = [s.model_dump() for s in result.sections]
        if result.llm_prompt_version and llm is not None:
            job.provider = llm.cfg.primary
            job.model = llm.cfg.gemini.models.small if llm.cfg.primary == "gemini" else None
            job.prompt_version = result.llm_prompt_version
        job.detail = {
            "sections": len(result.sections),
            "chunks": len(result.chunks),
            "warnings": result.warnings,
        }


def process_paper(
    paper_id: str,
    *,
    settings: Settings | None = None,
    session_factory: sessionmaker[Session] | None = None,
    llm: LLMClient | Callable[[], LLMClient | None] | None = None,
    stages: tuple[str, ...] = STAGES,
) -> str:
    """Run the requested stages. Never raises: failures are recorded on the job and paper."""
    from app.db import get_sessionmaker

    settings = settings or get_settings()
    factory = session_factory or get_sessionmaker()
    with factory() as session:
        paper = session.get(Paper, paper_id)
        if paper is None:
            log.error("process_paper: unknown paper %s", paper_id)
            return "missing"
        paper.status, paper.error = "processing", None
        session.commit()
        try:
            doc: ParsedDocument | None
            if "parse" in stages:
                doc = run_parse(session, settings, paper)
            else:
                doc = load_document(session, paper_id)
                if doc is None:
                    raise RuntimeError("no parse result to structure; run parse first")
            if "structure" in stages:
                client = llm() if callable(llm) else llm
                run_structure(session, paper, doc, client)
        except Exception as exc:
            log.exception("pipeline failed for %s", paper_id)
            paper = session.merge(paper)
            paper.status, paper.error = "failed", f"{type(exc).__name__}: {exc}"
            session.commit()
            return "failed"
        paper.status = "ready"
        session.commit()
        return "ready"


def stage_statuses(session: Session, paper_id: str) -> dict[str, dict[str, Any]]:
    """Latest job per stage, for the API / UI timeline."""
    jobs = session.scalars(
        select(Job).where(Job.paper_id == paper_id).order_by(Job.created_at)
    ).all()
    out: dict[str, dict[str, Any]] = {}
    for job in jobs:  # later jobs overwrite earlier ones
        out[job.stage] = {
            "status": job.status,
            "error": job.error,
            "started_at": job.started_at,
            "finished_at": job.finished_at,
            "provider": job.provider,
            "model": job.model,
            "prompt_version": job.prompt_version,
            "detail": job.detail,
        }
    return out
