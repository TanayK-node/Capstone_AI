"""Papers, pipeline jobs and parse outputs (SCOPE.md §6 database tables)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.types import JSONType


def _now() -> datetime:
    return datetime.now(UTC)


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # sha256 of the PDF bytes
    source_type: Mapped[str] = mapped_column(String(32))
    source_id: Mapped[str | None] = mapped_column(String(512), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    # "metadata" is reserved on declarative classes, hence the attribute name.
    meta: Mapped[dict[str, Any]] = mapped_column("metadata", JSONType, default=dict)
    status: Mapped[str] = mapped_column(String(16), default="queued")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )


class Job(Base):
    """One run of one pipeline stage for one paper."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    paper_id: Mapped[str] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"), index=True)
    stage: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16), default="queued")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # What produced the result (CLAUDE.md rule 8): parser or LLM provider/model/prompt version.
    provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    detail: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ParseResult(Base):
    """Document-level parse output; blocks live in their own table."""

    __tablename__ = "parse_results"

    paper_id: Mapped[str] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True
    )
    parser: Mapped[str] = mapped_column(String(32))
    parser_version: Mapped[str] = mapped_column(String(64))
    pages: Mapped[list[dict[str, Any]]] = mapped_column(JSONType, default=list)
    doc_metadata: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict)
    references: Mapped[list[dict[str, Any]]] = mapped_column(JSONType, default=list)
    warnings: Mapped[list[str]] = mapped_column(JSONType, default=list)
    sections: Mapped[list[dict[str, Any]]] = mapped_column(JSONType, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class BlockRow(Base):
    __tablename__ = "blocks"

    paper_id: Mapped[str] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True
    )
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    type: Mapped[str] = mapped_column(String(16))
    order: Mapped[int] = mapped_column(Integer)
    page: Mapped[int] = mapped_column(Integer)
    bbox: Mapped[dict[str, Any] | None] = mapped_column(JSONType, nullable=True)
    boxes: Mapped[list[dict[str, Any]]] = mapped_column(JSONType, default=list)
    section_path: Mapped[list[str]] = mapped_column(JSONType, default=list)
    role: Mapped[str | None] = mapped_column(String(32), nullable=True)
    label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    text: Mapped[str] = mapped_column(Text)
    data: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict)  # sentences, table


class ChunkRow(Base):
    """Hierarchical chunks (section > paragraph > sentence). Embeddings arrive in Phase 5."""

    __tablename__ = "chunks"

    paper_id: Mapped[str] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True
    )
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    level: Mapped[str] = mapped_column(String(16))
    parent_id: Mapped[str | None] = mapped_column(String(48), nullable=True)
    order: Mapped[int] = mapped_column(Integer)
    block_ids: Mapped[list[str]] = mapped_column(JSONType, default=list)
    section_path: Mapped[list[str]] = mapped_column(JSONType, default=list)
    role: Mapped[str | None] = mapped_column(String(32), nullable=True)
    page: Mapped[int] = mapped_column(Integer)
    boxes: Mapped[list[dict[str, Any]]] = mapped_column(JSONType, default=list)
    text: Mapped[str] = mapped_column(Text)


class ExtractionRow(Base):
    """Latest extraction for a paper (overwritten on re-run: stages are idempotent)."""

    __tablename__ = "extractions"

    paper_id: Mapped[str] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True
    )
    data: Mapped[dict[str, Any]] = mapped_column(JSONType)  # PaperExtraction
    provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(256), nullable=True)
    grounding_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ReproReport(Base):
    """Latest reproducibility scorecard for a paper (SCOPE.md §6 repro_reports)."""

    __tablename__ = "repro_reports"

    paper_id: Mapped[str] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True
    )
    score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100
    data: Mapped[dict[str, Any]] = mapped_column(JSONType)  # Scorecard
    checklist_version: Mapped[int] = mapped_column(Integer)
    provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ClaimReportRow(Base):
    """Latest claim verification for a paper (SCOPE.md §6 claim_reports)."""

    __tablename__ = "claim_reports"

    paper_id: Mapped[str] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True
    )
    data: Mapped[dict[str, Any]] = mapped_column(JSONType)  # ClaimReport
    provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class CodeReportRow(Base):
    """Latest paper-code comparison for a paper (SCOPE.md §6 code_reports)."""

    __tablename__ = "code_reports"

    paper_id: Mapped[str] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True
    )
    repo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32))
    data: Mapped[dict[str, Any]] = mapped_column(JSONType)  # CodeReport
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ChunkVector(Base):
    """Passage embedding for chat retrieval (M11). Stored as float32 bytes: a paper has at most
    a few hundred passages, scored in numpy, so pgvector is not needed (and SQLite tests work)."""

    __tablename__ = "chunk_vectors"

    paper_id: Mapped[str] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True
    )
    chunk_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    model: Mapped[str] = mapped_column(String(128))
    dim: Mapped[int] = mapped_column(Integer)
    vector: Mapped[bytes] = mapped_column(LargeBinary)


class MathReportRow(Base):
    """Equations and notation glossary for a paper (M10)."""

    __tablename__ = "math_reports"

    paper_id: Mapped[str] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True
    )
    data: Mapped[dict[str, Any]] = mapped_column(JSONType)  # MathReport
    provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ContextReportRow(Base):
    """Citation graph and novelty positioning for a paper (M12)."""

    __tablename__ = "context_reports"

    paper_id: Mapped[str] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True
    )
    data: Mapped[dict[str, Any]] = mapped_column(JSONType)  # ContextReport
    provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
