"""Word (.docx) report of one paper: a summary first, then every extracted field with its
evidence, then the analyses (reproducibility, claims, code, notation, results tables).

A pure function over the stored results (no LLM): the summary is assembled from extracted
items, so every sentence in it carries a page reference (CLAUDE.md rule 5).
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from datetime import UTC, datetime

import docx
from docx.document import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Pt, RGBColor
from docx.text.paragraph import Paragraph

from app.pipeline.export import SECTIONS
from app.schemas.claims import ClaimReport
from app.schemas.code import CodeReport
from app.schemas.extraction import Dataset, Evidence, Hyperparameter, Item, PaperExtraction
from app.schemas.math import MathReport
from app.schemas.repro import Scorecard
from app.schemas.results import ResultsTable
from app.schemas.review import Review, ReviewPoint

STATUS_TEXT = {
    "verified": "verified",
    "partial": "partly supported",
    "unsupported": "not supported by its quote",
    "unlocated": "quote not found in the paper",
    "unchecked": "not checked",
}
GREY = RGBColor(0x55, 0x55, 0x55)
MAX_TABLES = 8  # results tables included in full
SUMMARY_FIELDS = ("problem", "contributions", "method_summary", "novelty", "limitations")


@dataclass
class PaperBundle:
    paper_id: str
    title: str
    extraction: PaperExtraction
    source_url: str | None = None
    scorecard: Scorecard | None = None
    claims: ClaimReport | None = None
    code: CodeReport | None = None
    math: MathReport | None = None
    tables: list[ResultsTable] = field(default_factory=list)
    review: Review | None = None
    model: str | None = None


def _pages(evidence: list[Evidence]) -> str:
    pages = sorted({e.page for e in evidence})
    return ("p. " if len(pages) == 1 else "pp. ") + ", ".join(map(str, pages)) if pages else ""


def _status(evidence: list[Evidence]) -> str:
    for s in ("verified", "partial", "unsupported", "unlocated", "unchecked"):
        if any(e.grounding_status == s for e in evidence):
            return STATUS_TEXT[s]
    return "no evidence"


def _grey(par: Paragraph, text: str, *, italic: bool = False, size: float = 8.5) -> None:
    run = par.add_run(text)
    run.font.size = Pt(size)
    run.font.color.rgb = GREY
    run.italic = italic


def _label(item: Item) -> str:
    if isinstance(item, Hyperparameter):
        scope = f" ({item.scope})" if item.scope else ""
        return f"{item.name}{scope}: {item.value_raw or item.value}"
    if isinstance(item, Dataset) and item.name:
        extra = ", ".join(x for x in (item.split, item.size) if x)
        return f"{item.name} ({extra})" if extra else item.name
    return item.value


def _bullet(doc: Document, item: Item, *, quotes: bool = True) -> None:
    par = doc.add_paragraph(style="List Bullet")
    par.add_run(_label(item))
    if item.evidence:
        _grey(par, f"  [{_pages(item.evidence)}; {_status(item.evidence)}]")
    else:
        _grey(par, "  [no evidence: unverified]")
    if quotes:
        for ev in item.evidence[:1]:
            q = doc.add_paragraph()
            q.paragraph_format.left_indent = Pt(18)
            _grey(q, f"“{ev.quote}”", italic=True)


def _table(doc: Document, header: list[str] | None, rows: list[list[str]]) -> None:
    """A table; header=None for a two-column key / value table (keys in bold)."""
    cols = len(header) if header else len(rows[0])
    t = doc.add_table(rows=1 if header else 0, cols=cols)
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    if header:
        for cell, text in zip(t.rows[0].cells, header, strict=True):
            cell.text = text
            for run in cell.paragraphs[0].runs:
                run.bold = True
    for r in rows:
        cells = t.add_row().cells
        for cell, text in zip(cells, r, strict=True):
            cell.text = text
        if not header:
            for run in cells[0].paragraphs[0].runs:
                run.bold = True
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(8.5)
    doc.add_paragraph()


def build_docx(b: PaperBundle) -> bytes:
    doc = docx.Document()
    styles = doc.styles
    styles["Normal"].font.name = "Calibri"
    styles["Normal"].font.size = Pt(10.5)
    ex = b.extraction
    meta = ex.metadata

    doc.add_heading(meta.title or b.title or "Untitled paper", level=0)
    if meta.authors:
        doc.add_paragraph(", ".join(meta.authors))
    facts = [x for x in (meta.venue, meta.year) if x]
    facts += [f"arXiv:{meta.arxiv_id}"] if meta.arxiv_id else []
    facts += [f"doi:{meta.doi}"] if meta.doi else []
    facts += [b.source_url] if b.source_url else []
    if facts:
        doc.add_paragraph(" · ".join(facts))
    note = doc.add_paragraph()
    _grey(note, f"Generated by PaperLens on {datetime.now(UTC):%Y-%m-%d}"
          + (f" ({b.model})" if b.model else "") + ". Every item cites the page its evidence "
          "comes from; items marked “quote not found” or “no evidence” are "
          "unverified and should be checked against the paper.")  # fmt: skip

    # ---- summary
    doc.add_heading("Summary", level=1)
    for name in SUMMARY_FIELDS:
        items: list[Item] = getattr(ex, name)
        if not items:
            continue
        heading = dict(SECTIONS).get(name, name)
        doc.add_heading(heading, level=3)
        for item in items[:4]:
            _bullet(doc, item, quotes=False)
    glance: list[list[str]] = []
    for name, label in (("task", "Task"), ("datasets", "Datasets"), ("metrics", "Metrics"),
                        ("baselines", "Baselines")):  # fmt: skip
        values = [_label(i) for i in getattr(ex, name)]
        if values:
            glance.append([label, "; ".join(values[:12]) + (" …" if len(values) > 12 else "")])
    if b.scorecard is not None and b.scorecard.score is not None:
        glance.append(["Reproducibility", f"{b.scorecard.score:.0f}/100"])
    if b.claims is not None and b.claims.counts:
        verdicts = ", ".join(f"{v} {k.replace('_', ' ')}" for k, v in b.claims.counts.items())
        glance.append(["Claims checked", verdicts])
    if b.code is not None:
        repo = (
            b.code.repo.url if b.code.repo else (ex.code_urls[0].value if ex.code_urls else "none")
        )
        counts = ", ".join(f"{v} {k.replace('_', ' ')}" for k, v in b.code.counts.items())
        glance.append(["Code", f"{repo} ({b.code.status.replace('_', ' ')}"
                               + (f"; {counts}" if counts else "") + ")"])  # fmt: skip
    if glance:
        doc.add_heading("At a glance", level=3)
        _table(doc, None, glance)

    # ---- every extracted field
    doc.add_heading("Extracted information", level=1)
    for name, heading in SECTIONS:
        items = getattr(ex, name)
        if not items or name == "claims":
            continue
        doc.add_heading(heading, level=2)
        if name == "hyperparameters":
            _table(doc, ["Hyperparameter", "Value", "Scope", "Page", "Evidence"],
                   [[h.name, h.value_raw or h.value, h.scope, _pages(h.evidence),
                     _status(h.evidence)] for h in ex.hyperparameters])  # fmt: skip
            continue
        if name == "datasets":
            _table(doc, ["Dataset", "Split", "Size", "Page", "Evidence"],
                   [[d.name or d.value, d.split, d.size, _pages(d.evidence), _status(d.evidence)]
                    for d in ex.datasets])  # fmt: skip
            continue
        for item in items:
            _bullet(doc, item)

    # ---- reviewer mode
    if b.review is not None:
        rv = b.review
        doc.add_heading("Review (reviewer mode)", level=1)
        _grey(doc.add_paragraph(), "Written by the LLM from the paper and the analyses; facts "
              "from the analyses were established in Python. No score is given.")  # fmt: skip
        doc.add_paragraph(rv.summary)
        sections: list[tuple[str, list[ReviewPoint]]] = [
            ("Strengths", rv.strengths), ("Weaknesses", rv.weaknesses),
            ("Missing ablations", rv.missing_ablations)]  # fmt: skip
        for title, points in sections:
            if points:
                doc.add_heading(title, level=3)
                for pt in points:
                    par = doc.add_paragraph(style="List Bullet")
                    par.add_run(pt.point)
                    if pt.evidence:
                        _grey(par, f"  [{_pages(pt.evidence)}; {_status(pt.evidence)}]")
        if rv.findings:
            doc.add_heading("Facts from the analyses", level=3)
            for f in rv.findings:
                doc.add_paragraph(f"[{f.source}] {f.text}", style="List Bullet")
        if rv.questions:
            doc.add_heading("Questions for the authors", level=3)
            for q in rv.questions:
                doc.add_paragraph(q, style="List Number")

    # ---- analyses
    if b.claims is not None and b.claims.claims:
        doc.add_heading("Claims checked against the tables", level=1)
        _table(doc, ["Claim", "Verdict", "Why (computed in Python)", "Page"],
               [[c.text, c.verdict.replace("_", " "), c.explanation, _pages(c.evidence)]
                for c in b.claims.claims])  # fmt: skip
    if b.scorecard is not None:
        sc = b.scorecard
        score = "n/a" if sc.score is None else f"{sc.score:.0f}/100"
        doc.add_heading(f"Reproducibility scorecard: {score}", level=1)
        _table(doc, ["Item", "Status", "Note", "Page"],
               [[i.description, i.status.replace("_", " "), i.note, _pages(i.evidence)]
                for i in sc.items])  # fmt: skip
    if b.code is not None and b.code.comparisons:
        doc.add_heading("Paper vs code", level=1)
        p = doc.add_paragraph()
        _grey(p, "Static analysis of the repository (nothing was run).")
        _table(doc, ["Hyperparameter", "Status", "Paper", "Code (file:line)"],
               [[c.paper_name or c.canonical, c.status.replace("_", " "), c.paper_value,
                 "; ".join(f"{v.value} ({v.file}:{v.line or ''})" for v in c.code_values[:3])]
                for c in b.code.comparisons if c.status != "only_in_code"])  # fmt: skip
    if b.math is not None and b.math.symbols:
        doc.add_heading("Notation", level=1)
        _table(doc, ["Symbol", "Meaning", "Page", "Evidence"],
               [[s.symbol, s.meaning, _pages(s.evidence), _status(s.evidence)]
                for s in b.math.symbols])  # fmt: skip
    if b.tables:
        doc.add_heading("Results tables", level=1)
        for t in b.tables[:MAX_TABLES]:
            cap = doc.add_paragraph()
            cap.add_run(f"{t.label or 'Table'} (p. {t.page}). ").bold = True
            cap.add_run(t.caption[:300])
            # Label columns hold no cells (their text is the row label).
            used = {c.col for r in t.rows for c in r.cells}
            cols = [c for c in t.columns if c.index in used]
            first = next((c.header for c in t.columns if c.index not in used and c.header), "")
            header = [first, *[(f"{c.group} / " if c.group else "") + c.header for c in cols]]
            rows = []
            for r in t.rows:
                cells = {c.col: c.text + (" *" if c.is_best else "") for c in r.cells}
                label = r.label + (" (proposed)" if r.is_proposed else "")
                rows.append([label, *[cells.get(c.index, "") for c in cols]])
            _table(doc, header, rows)
            _grey(doc.add_paragraph(), "* best in its column (direction from the header)")
        if len(b.tables) > MAX_TABLES:
            doc.add_paragraph(f"{len(b.tables) - MAX_TABLES} more tables: see the CSV export.")

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
