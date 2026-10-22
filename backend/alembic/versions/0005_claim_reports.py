"""Phase 4: claim verification reports.

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "claim_reports",
        sa.Column(
            "paper_id",
            sa.String(64),
            sa.ForeignKey("papers.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("data", sa.JSON().with_variant(JSONB(), "postgresql"), nullable=False),
        sa.Column("provider", sa.String(32)),
        sa.Column("model", sa.String(128)),
        sa.Column("prompt_version", sa.String(256)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("claim_reports")
