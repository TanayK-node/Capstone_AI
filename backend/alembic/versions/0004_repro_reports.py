"""Phase 3: reproducibility scorecards.

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "repro_reports",
        sa.Column(
            "paper_id",
            sa.String(64),
            sa.ForeignKey("papers.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("score", sa.Float()),
        sa.Column("data", sa.JSON().with_variant(JSONB(), "postgresql"), nullable=False),
        sa.Column("checklist_version", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(32)),
        sa.Column("model", sa.String(128)),
        sa.Column("prompt_version", sa.String(256)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("repro_reports")
