"""Reviewer mode (F15): one LLM call writes the review; Python supplies the facts.

1. Facts from the analyses, in Python: missing reproducibility items, claims the tables
   contradict or do not support, hyperparameters the code sets differently. They go to the
   model as given and are shown apart from its text, so the review cannot misstate them.
2. One LLM call over the paper text (abstract to conclusion, tagged with block ids), the
   extracted overview and the facts: summary, strengths, weaknesses, missing ablations,
   questions. No score: a rating is a verdict the LLM must not give (CLAUDE.md rule 4).
3. Each point's quote is grounded like extraction evidence; unfound quotes stay, marked
   "unlocated" (rule 5).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pymupdf

from app import prompts
from app.llm.client import LLMClient
from app.pipeline.extract.groups import render_block
from app.pipeline.verify.grounding import attach_location
from app.schemas.claims import ClaimReport
from app.schemas.code import CodeReport
from app.schemas.document import Block, ParsedDocument
from app.schemas.extraction import Evidence, PaperExtraction
from app.schemas.repro import Scorecard
from app.schemas.review import Finding, PointOut, Review, ReviewOut, ReviewPoint

TEXT_ROLES = {"abstract", "introduction", "method", "experiments", "results", "ablation",
              "limitations", "conclusion", "discussion"}  # fmt: skip
OVERVIEW = ("problem", "contributions", "method_summary", "novelty", "datasets", "baselines",
            "metrics", "ablations", "limitations")  # fmt: skip


@dataclass
class ReviewRun:
    review: Review
    llm_calls: int = 0
    prompt_version: str | None = None
    provider: str | None = None
    model: str | None = None
    warnings: list[str] = field(default_factory=list)


def findings(scorecard: Scorecard | None, claims: ClaimReport | None,
             code: CodeReport | None) -> list[Finding]:  # fmt: skip
    out: list[Finding] = []
    if scorecard is not None:
        missing = [i for i in scorecard.items if i.status == "missing"]
        for item in sorted(missing, key=lambda i: -i.weight)[:6]:
            out.append(Finding(source="reproducibility", text=f"Not stated: {item.description}"))
    if claims is not None:
        for c in claims.claims:
            if c.verdict in ("contradicted", "unsupported"):
                out.append(Finding(source="claims", evidence=c.evidence,
                                   text=f"Claim {c.verdict} by the tables: “{c.text}” "
                                        f"({c.explanation})"))  # fmt: skip
    if code is not None:
        for cmp in code.comparisons:
            if cmp.status == "mismatch":
                vals = ", ".join(sorted({v.value for v in cmp.code_values})[:3])
                out.append(Finding(source="code", evidence=cmp.paper_evidence,
                                   text=f"{cmp.paper_name or cmp.canonical}: paper "
                                        f"{cmp.paper_value}, code {vals}"))  # fmt: skip
    return out


def review_text(doc: ParsedDocument, max_chars: int) -> str:
    chosen = [b for b in doc.blocks if b.type in ("paragraph", "table")
              and (b.role or "") in TEXT_ROLES]  # fmt: skip
    parts: list[str] = []
    used = 0
    for block in chosen:
        piece = render_block(block)
        if used + len(piece) > max_chars:
            break
        parts.append(piece)
        used += len(piece) + 2
    return "\n\n".join(parts)


def _overview(ex: PaperExtraction) -> list[str]:
    lines = []
    for name in OVERVIEW:
        values = [i.value for i in getattr(ex, name)][:6]
        if values:
            lines.append(f"{name.replace('_', ' ')}: " + " | ".join(values))
    return lines


def build_review(
    doc: ParsedDocument,
    extraction: PaperExtraction,
    client: LLMClient,
    *,
    scorecard: Scorecard | None,
    claims: ClaimReport | None,
    code: CodeReport | None,
    pdf_path: Path | None,
    max_chars: int = 40_000,
) -> ReviewRun:
    facts = findings(scorecard, claims, code)
    prompt = prompts.render(
        "review",
        findings=[f.model_dump() for f in facts],
        overview=_overview(extraction),
        text=review_text(doc, max_chars),
    )
    result = client.generate_json(prompt, ReviewOut, role="extraction")
    out = result.value
    blocks = {b.id: b for b in doc.blocks}
    pdf = pymupdf.open(pdf_path) if pdf_path and pdf_path.exists() else None
    try:
        review = Review(
            summary=out.summary.strip(),
            strengths=[_point(p, blocks, pdf) for p in out.strengths],
            weaknesses=[_point(p, blocks, pdf) for p in out.weaknesses],
            missing_ablations=[_point(p, blocks, pdf) for p in out.missing_ablations],
            questions=[q.strip() for q in out.questions if q.strip()],
            findings=facts,
        )
    finally:
        if pdf is not None:
            pdf.close()
    return ReviewRun(review, llm_calls=0 if result.meta.cached else 1,
                     prompt_version=prompt.id, provider=result.meta.provider,
                     model=result.meta.model)  # fmt: skip


def _point(p: PointOut, blocks: dict[str, Block], pdf: pymupdf.Document | None) -> ReviewPoint:
    evidence: list[Evidence] = []
    if p.quote.strip():
        chunk = p.chunk_id.strip().strip("[]")
        ev = Evidence(chunk_id=chunk, page=blocks[chunk].page if chunk in blocks else 1,
                      quote=p.quote.strip())  # fmt: skip
        if attach_location(ev, blocks, pdf):
            ev.grounding_status = "verified"  # the sentence is in the paper
        evidence.append(ev)
    return ReviewPoint(point=p.point.strip(), evidence=evidence)
