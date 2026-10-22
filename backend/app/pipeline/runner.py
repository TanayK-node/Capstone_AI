"""Stage runner: Parse -> Structure -> Extract -> Verify -> Repro for one paper.

Every stage is idempotent (CLAUDE.md rule 8): it deletes its previous output for the paper
before writing, and records a Job row with what produced the result.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings, get_settings
from app.llm.client import LLMClient
from app.models import (
    BlockRow,
    ChunkRow,
    ClaimReportRow,
    CodeReportRow,
    ExtractionRow,
    Job,
    Paper,
    ParseResult,
    ReproReport,
)
from app.pipeline.claims.service import check_claims
from app.pipeline.code_check.service import check_code
from app.pipeline.extract.extractor import extract_document
from app.pipeline.ingest import storage
from app.pipeline.parse import get_parser
from app.pipeline.repro.analyzer import analyze
from app.pipeline.repro.checklist import load_checklist
from app.pipeline.repro.github import GitHubClient
from app.pipeline.results.builder import build_results, proposed_names, result_entries
from app.pipeline.structure.sections import structure_document
from app.pipeline.verify.grounding import ground, grounding_score
from app.schemas.document import (
    Block,
    DocumentMetadata,
    PageInfo,
    ParsedDocument,
    Reference,
    Sentence,
    TableData,
)
from app.schemas.extraction import PaperExtraction

log = logging.getLogger("paperlens.pipeline")

STAGES = ("parse", "structure", "extract", "verify", "repro", "claims", "code")
ANALYSIS_STAGES = ("extract", "verify", "repro", "claims", "code")
# What each analysis stage reads: when one of these failed in this run, the stage is skipped.
NEEDS: dict[str, set[str]] = {
    "verify": {"extract"},
    "repro": {"extract", "verify"},
    "claims": {"extract"},
    "code": {"extract"},
}
# Stages after these are "analysis": if one fails the paper is still usable ("partial").
CORE_STAGES = ("parse", "structure")


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
            role=r.role,
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


def _require_llm(llm: LLMClient | None) -> LLMClient:
    if llm is None or not llm.providers:
        raise RuntimeError("no LLM provider configured: set GEMINI_API_KEY in .env")
    return llm


def run_extract(
    session: Session, settings: Settings, paper: Paper, doc: ParsedDocument, llm: LLMClient | None
) -> None:
    with stage_job(session, paper.id, "extract") as job:
        client = _require_llm(llm)
        run = extract_document(
            doc,
            client,
            metadata={**(paper.meta or {}), "source_url": paper.source_url},
            max_group_chars=settings.extraction.max_group_chars,
            parallel_calls=settings.extraction.parallel_calls,
            retry_failed_after_s=settings.extraction.retry_failed_after_s,
        )
        job.detail = {
            "groups": [g.__dict__ for g in run.groups],
            "llm_calls": run.calls,
            "items": len(run.extraction.all_items()),
            "result_values": len(run.extraction.results),
        }
        if run.all_failed:
            errors = "; ".join(f"{g.name}: {g.error}" for g in run.groups if g.error)
            raise RuntimeError(f"every extraction call failed ({errors})")
        # Results tables are deterministic (M9); stored with the extraction they label.
        run.extraction.results = result_entries(build_results(doc, run.extraction), run.extraction)
        done = [g for g in run.groups if g.status == "done"]
        job.provider = done[0].provider if done else None
        # Several models when a group fell back to the overload backup (e.g. Flash-Lite).
        job.model = ",".join(dict.fromkeys(g.model for g in done if g.model)) or None
        job.prompt_version = ",".join(g.prompt_version for g in done if g.prompt_version)
        session.merge(
            ExtractionRow(
                paper_id=paper.id,
                data=run.extraction.model_dump(mode="json"),
                provider=job.provider,
                model=job.model,
                prompt_version=job.prompt_version,
                grounding_score=None,
                verified=False,
                created_at=datetime.now(UTC),
            )
        )


def run_verify(
    session: Session, settings: Settings, paper: Paper, doc: ParsedDocument, llm: LLMClient | None
) -> None:
    with stage_job(session, paper.id, "verify") as job:
        row = session.get(ExtractionRow, paper.id)
        if row is None:
            raise RuntimeError("nothing to verify: the extract stage has not produced results")
        extraction = PaperExtraction.model_validate(row.data)
        client = llm if llm is not None and llm.providers else None
        run = ground(extraction, doc, client, storage.pdf_path(settings, paper.id))
        score = grounding_score(extraction)
        row.data = extraction.model_dump(mode="json")
        row.grounding_score = score
        row.verified = True
        job.provider, job.model, job.prompt_version = run.provider, run.model, run.prompt_version
        job.detail = {
            "located": run.located,
            "unlocated": run.unlocated,
            "support_checked": run.checked,
            "llm_calls": run.support_calls,
            "grounding_score": score,
            "warnings": run.warnings,
        }


def make_github(settings: Settings) -> GitHubClient | None:
    if not settings.repro.github_check:
        return None
    token = settings.github_token.get_secret_value() if settings.github_token else None
    return GitHubClient(token or None, timeout_s=settings.repro.github_timeout_s)


def run_repro(
    session: Session, settings: Settings, paper: Paper, doc: ParsedDocument, llm: LLMClient | None
) -> None:
    with stage_job(session, paper.id, "repro") as job:
        row = session.get(ExtractionRow, paper.id)
        if row is None:
            raise RuntimeError("no extraction to score: run extract and verify first")
        extraction = PaperExtraction.model_validate(row.data)
        checklist = load_checklist()
        github = make_github(settings)
        try:
            run = analyze(
                doc,
                extraction,
                checklist,
                client=llm if llm is not None and llm.providers else None,
                github=github,
                pdf_path=storage.pdf_path(settings, paper.id),
                max_chars=settings.repro.max_context_chars,
            )
        finally:
            if github is not None:
                github.close()
        card = run.scorecard
        session.merge(
            ReproReport(
                paper_id=paper.id,
                score=card.score,
                data=card.model_dump(mode="json"),
                checklist_version=checklist.version,
                provider=run.provider,
                model=run.model,
                prompt_version=run.prompt_version,
                created_at=datetime.now(UTC),
            )
        )
        job.provider, job.model, job.prompt_version = run.provider, run.model, run.prompt_version
        statuses: dict[str, int] = {}
        for item in card.items:
            statuses[item.status] = statuses.get(item.status, 0) + 1
        job.detail = {
            "score": card.score,
            "checklist_version": checklist.version,
            "statuses": statuses,
            "by_source": {
                src: sum(1 for i in card.items if i.source == src)
                for src in ("rule", "extraction", "repo", "llm")
            },
            "llm_items": run.llm_items,
            "llm_calls": run.llm_calls,
            "repo": card.repo.url if card.repo else None,
            "warnings": run.warnings,
        }


def run_claims(
    session: Session, settings: Settings, paper: Paper, doc: ParsedDocument, llm: LLMClient | None
) -> None:
    with stage_job(session, paper.id, "claims") as job:
        row = session.get(ExtractionRow, paper.id)
        if row is None:
            raise RuntimeError("no extraction: run extract first")
        extraction = PaperExtraction.model_validate(row.data)
        tables = build_results(doc, extraction)
        client = llm if llm is not None and llm.providers else None
        run = check_claims(extraction, tables, client, settings.claims.tolerance)
        session.merge(
            ClaimReportRow(
                paper_id=paper.id,
                data=run.report.model_dump(mode="json"),
                provider=run.provider,
                model=run.model,
                prompt_version=run.prompt_version,
                created_at=datetime.now(UTC),
            )
        )
        job.provider, job.model, job.prompt_version = run.provider, run.model, run.prompt_version
        job.detail = {
            "claims": len(run.report.claims),
            "verdicts": run.report.counts,
            "tables": len(tables),
            "llm_calls": run.llm_calls,
            "warnings": run.warnings,
        }


def run_code(
    session: Session, settings: Settings, paper: Paper, doc: ParsedDocument, llm: LLMClient | None
) -> None:
    """Paper-code consistency (M7). No LLM: discovery, clone, static scan, comparison."""
    with stage_job(session, paper.id, "code") as job:
        row = session.get(ExtractionRow, paper.id)
        if row is None:
            raise RuntimeError("no extraction: run extract first")
        extraction = PaperExtraction.model_validate(row.data)
        cfg = settings.code_check
        github = make_github(settings)
        try:
            report = check_code(
                extraction,
                Path(settings.app.data_dir) / "code" / paper.id,
                method_names=proposed_names(doc, extraction),
                github=github,
                user_repo=(paper.meta or {}).get("code_repo"),
                sandbox=cfg.sandbox,
                clone_timeout_s=cfg.clone_timeout_s,
                max_repo_mb=cfg.max_repo_mb,
                search=cfg.search_github,
            )
        finally:
            if github is not None:
                github.close()
        session.merge(
            CodeReportRow(
                paper_id=paper.id,
                repo_url=report.candidates[0].url if report.candidates else None,
                status=report.status,
                data=report.model_dump(mode="json"),
                created_at=datetime.now(UTC),
            )
        )
        job.provider = report.sandbox
        job.model = report.commit[:12] if report.commit else None
        job.detail = {
            "status": report.status,
            "repo": report.candidates[0].url if report.candidates else None,
            "confidence": report.candidates[0].confidence if report.candidates else None,
            "files_scanned": report.files_scanned,
            "params_found": report.params_found,
            "comparisons": report.counts,
            "sandbox": report.sandbox,
            "warnings": report.warnings,
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
            client = llm() if callable(llm) else llm
            if "structure" in stages:
                run_structure(session, paper, doc, client)
        except Exception as exc:
            log.exception("pipeline failed for %s", paper_id)
            paper = session.merge(paper)
            paper.status, paper.error = "failed", f"{type(exc).__name__}: {exc}"
            session.commit()
            return "failed"

        # Analysis stages: a failure keeps the parsed paper usable ("partial"), never blank.
        errors: list[str] = []
        if any(st in stages for st in ANALYSIS_STAGES):
            doc = load_document(session, paper_id) or doc  # now with section roles
        analysis = (
            ("extract", run_extract),
            ("verify", run_verify),
            ("repro", run_repro),
            ("claims", run_claims),
            ("code", run_code),
        )
        failed: set[str] = set()
        for name, fn in analysis:
            if name not in stages:
                continue
            if failed & NEEDS.get(name, set()):
                continue  # it builds on a stage that just failed
            try:
                fn(session, settings, paper, doc, client)
            except Exception as exc:
                log.warning("%s failed for %s: %s", name, paper_id, exc)
                paper = session.merge(paper)
                errors.append(f"{name}: {type(exc).__name__}: {exc}")
                failed.add(name)
        paper.status = "partial" if errors else "ready"
        paper.error = "; ".join(errors) or None
        session.commit()
        return paper.status


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
