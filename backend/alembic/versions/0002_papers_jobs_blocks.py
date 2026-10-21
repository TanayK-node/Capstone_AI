"""Phase 1: papers, jobs, parse_results, blocks, chunks.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

JSON = sa.JSON().with_variant(JSONB(), "postgresql")
TS = sa.DateTime(timezone=True)


def _paper_fk() -> sa.Column:  # type: ignore[type-arg]
    return sa.Column(
        "paper_id", sa.String(64), sa.ForeignKey("papers.id", ondelete="CASCADE"), nullable=False
    )


def upgrade() -> None:
    op.create_table(
        "papers",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("source_type", sa.String(32), nullable=False),
        sa.Column("source_id", sa.String(512)),
        sa.Column("source_url", sa.Text()),
        sa.Column("title", sa.Text()),
        sa.Column("metadata", JSON, nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("error", sa.Text()),
        sa.Column("page_count", sa.Integer(), nullable=False),
        sa.Column("created_at", TS, nullable=False),
        sa.Column("updated_at", TS, nullable=False),
    )
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        _paper_fk(),
        sa.Column("stage", sa.String(32), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("error", sa.Text()),
        sa.Column("started_at", TS),
        sa.Column("finished_at", TS),
        sa.Column("provider", sa.String(32)),
        sa.Column("model", sa.String(128)),
        sa.Column("prompt_version", sa.String(128)),
        sa.Column("detail", JSON, nullable=False),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_index("ix_jobs_paper_id", "jobs", ["paper_id"])
    op.create_table(
        "parse_results",
        sa.Column(
            "paper_id",
            sa.String(64),
            sa.ForeignKey("papers.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("parser", sa.String(32), nullable=False),
        sa.Column("parser_version", sa.String(64), nullable=False),
        sa.Column("pages", JSON, nullable=False),
        sa.Column("doc_metadata", JSON, nullable=False),
        sa.Column("references", JSON, nullable=False),
        sa.Column("warnings", JSON, nullable=False),
        sa.Column("sections", JSON, nullable=False),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_table(
        "blocks",
        _paper_fk(),
        sa.Column("id", sa.String(16), nullable=False),
        sa.Column("type", sa.String(16), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("page", sa.Integer(), nullable=False),
        sa.Column("bbox", JSON),
        sa.Column("boxes", JSON, nullable=False),
        sa.Column("section_path", JSON, nullable=False),
        sa.Column("role", sa.String(32)),
        sa.Column("label", sa.String(64)),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("data", JSON, nullable=False),
        sa.PrimaryKeyConstraint("paper_id", "id"),
    )
    op.create_table(
        "chunks",
        _paper_fk(),
        sa.Column("id", sa.String(48), nullable=False),
        sa.Column("level", sa.String(16), nullable=False),
        sa.Column("parent_id", sa.String(48)),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("block_ids", JSON, nullable=False),
        sa.Column("section_path", JSON, nullable=False),
        sa.Column("role", sa.String(32)),
        sa.Column("page", sa.Integer(), nullable=False),
        sa.Column("boxes", JSON, nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("paper_id", "id"),
    )


def downgrade() -> None:
    for table in ("chunks", "blocks", "parse_results", "jobs", "papers"):
        op.drop_table(table)
