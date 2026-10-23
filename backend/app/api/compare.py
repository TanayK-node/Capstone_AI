"""Multi-paper comparison matrix (F14)."""

from __future__ import annotations

import csv
import io
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.papers import get_session
from app.models import ClaimReportRow, CodeReportRow, ExtractionRow, Paper, ReproReport
from app.pipeline.compare import PaperData, build_comparison
from app.pipeline.results.builder import build_results, proposed_names
from app.pipeline.runner import load_document
from app.schemas.claims import ClaimReport
from app.schemas.code import CodeReport
from app.schemas.compare import Comparison
from app.schemas.extraction import PaperExtraction
from app.schemas.repro import Scorecard

router = APIRouter(prefix="/api/compare", tags=["compare"])
MAX_PAPERS = 10


@router.get("", response_model=None)
def compare(
    ids: list[str] = Query(..., description="2 to 10 paper ids"),
    format: Literal["json", "csv"] = Query("json"),
    session: Session = Depends(get_session),
) -> Comparison | Response:
    ids = list(dict.fromkeys(ids))
    if not 2 <= len(ids) <= MAX_PAPERS:
        raise HTTPException(422, f"pick 2 to {MAX_PAPERS} papers")
    papers: list[PaperData] = []
    for pid in ids:
        paper = session.get(Paper, pid)
        row = session.get(ExtractionRow, pid)
        doc = load_document(session, pid)
        if paper is None or row is None or doc is None:
            raise HTTPException(409, f"paper {pid[:12]} has no extraction yet")
        ex = PaperExtraction.model_validate(row.data)

        def stored(model: type[Any], schema: type[BaseModel], pid: str = pid) -> Any:
            r = session.get(model, pid)
            return schema.model_validate(r.data) if r is not None else None

        papers.append(PaperData(id=pid, title=paper.title or "", extraction=ex,
                                tables=build_results(doc, ex), method=proposed_names(doc, ex),
                                scorecard=stored(ReproReport, Scorecard),
                                claims=stored(ClaimReportRow, ClaimReport),
                                code=stored(CodeReportRow, CodeReport)))  # fmt: skip
    comp = build_comparison(papers)
    if format == "json":
        return comp
    disposition = 'attachment; filename="paperlens-compare.csv"'
    return Response(
        to_csv(comp),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": disposition},
    )


def to_csv(comp: Comparison) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["group", "item", *[p.title for p in comp.papers]])
    for r in comp.rows:
        w.writerow([r.group, r.label, *["; ".join(c.values) for c in r.cells]])
    for s in comp.results:
        w.writerow(
            ["Results", s.label, *[f"{c.text} ({c.method})" if c.text else "" for c in s.cells]]
        )
    return buf.getvalue()
