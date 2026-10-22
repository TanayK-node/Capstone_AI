"""Passages and their vectors in the database (index stage, chat requests)."""

from __future__ import annotations

import numpy as np
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import ChunkRow, ChunkVector
from app.pipeline.retrieval.embedder import Embedder, from_bytes, to_bytes
from app.pipeline.retrieval.search import PaperIndex, Passage

SKIP_ROLES = {"references", "acknowledgements"}
BATCH = 64


def load_passages(session: Session, paper_id: str) -> list[Passage]:
    rows = session.scalars(
        select(ChunkRow)
        .where(ChunkRow.paper_id == paper_id, ChunkRow.level == "paragraph")
        .order_by(ChunkRow.order)
    ).all()
    return [
        Passage(
            chunk_id=r.id,
            text=r.text,
            page=r.page,
            section=" > ".join(r.section_path[-2:]),
            boxes=r.boxes,
            role=r.role,
        )
        for r in rows
        if (r.role or "") not in SKIP_ROLES and r.text.strip()
    ]


def build_vectors(session: Session, paper_id: str, embedder: Embedder) -> int:
    """(Re)embed every passage of the paper. Idempotent: old vectors are replaced."""
    passages = load_passages(session, paper_id)
    session.execute(delete(ChunkVector).where(ChunkVector.paper_id == paper_id))
    for start in range(0, len(passages), BATCH):
        batch = passages[start : start + BATCH]
        vectors = embedder.embed([p.text[:2000] for p in batch])
        session.add_all(
            ChunkVector(
                paper_id=paper_id,
                chunk_id=p.chunk_id,
                model=embedder.model_name,
                dim=int(v.shape[0]),
                vector=to_bytes(v),
            )
            for p, v in zip(batch, vectors, strict=True)
        )
    return len(passages)


def load_index(session: Session, paper_id: str, embedder: Embedder | None) -> PaperIndex:
    """Passages plus their vectors, when they exist for the embedder's model."""
    passages = load_passages(session, paper_id)
    vectors: np.ndarray | None = None
    if embedder is not None and passages:
        rows = {
            r.chunk_id: r
            for r in session.scalars(
                select(ChunkVector).where(
                    ChunkVector.paper_id == paper_id, ChunkVector.model == embedder.model_name
                )
            )
        }
        if all(p.chunk_id in rows for p in passages):
            vectors = np.vstack(
                [from_bytes(rows[p.chunk_id].vector, rows[p.chunk_id].dim) for p in passages]
            )
    return PaperIndex(passages, vectors)
