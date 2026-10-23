"""Multi-paper comparison matrix (F14). No LLM: built from stored extractions and analyses.

Rows:
- Datasets / Metrics / Baselines: one row per distinct item across the papers (names merged
  with extract.normalize.same_item, but never across different numbers: ImageNet is not
  ImageNet-21k), with the page each paper states it on. Shared rows first.
- Training: the main hyperparameters by canonical name (code_check's synonym table).
- Compute, code link, reproducibility score, claim verdicts.
Shared results: table columns whose header reads the same in two or more papers ("BLEU
EN-DE"), with each paper's own method's best value. Matching is by header text only, so
the setups may still differ; the UI says so.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.pipeline.code_check.compare import canonical_paper
from app.pipeline.extract.normalize import same_item
from app.schemas.claims import ClaimReport
from app.schemas.code import CodeReport
from app.schemas.compare import (
    Cell,
    ComparedPaper,
    Comparison,
    MatrixRow,
    ResultCell,
    SharedResult,
)
from app.schemas.extraction import Item, PaperExtraction
from app.schemas.repro import Scorecard
from app.schemas.results import ResultsTable

TRAINING = ("optimizer", "learning_rate", "batch_size", "epochs", "train_steps", "warmup_steps",
            "weight_decay", "dropout", "label_smoothing")  # fmt: skip
MAX_ROWS_PER_GROUP = 40


@dataclass
class PaperData:
    id: str
    title: str
    extraction: PaperExtraction
    tables: list[ResultsTable]
    method: list[str]
    scorecard: Scorecard | None = None
    claims: ClaimReport | None = None
    code: CodeReport | None = None


def _same(a: str, b: str) -> bool:
    return re.findall(r"\d+", a.lower()) == re.findall(r"\d+", b.lower()) and same_item(a, b)


def _pages(items: list[Item]) -> list[int]:
    return sorted({e.page for i in items for e in i.evidence})


def _entity_rows(group: str, field: str, papers: list[PaperData]) -> list[MatrixRow]:
    clusters: list[tuple[str, list[list[Item]]]] = []  # (label, items per paper)
    for k, p in enumerate(papers):
        for item in getattr(p.extraction, field):
            name = getattr(item, "name", "") or item.value
            for label, per_paper in clusters:
                if _same(label, name):
                    per_paper[k].append(item)
                    break
            else:
                per_paper = [[] for _ in papers]
                per_paper[k].append(item)
                clusters.append((name, per_paper))
    rows = [
        MatrixRow(group=group, label=label,
                  cells=[Cell(values=["✓"] if items else [], pages=_pages(items))
                         for items in per_paper],
                  shared=sum(1 for items in per_paper if items) > 1)
        for label, per_paper in clusters
    ]  # fmt: skip
    rows.sort(key=lambda r: (not r.shared, -sum(1 for c in r.cells if c.values)))
    return rows[:MAX_ROWS_PER_GROUP]


def _training_rows(papers: list[PaperData]) -> list[MatrixRow]:
    rows = []
    for canon in TRAINING:
        cells = []
        for p in papers:
            hps = [h for h in p.extraction.hyperparameters
                   if (canonical_paper(h.name) or h.name.lower()) == canon]  # fmt: skip
            values = list(dict.fromkeys(
                (h.value_raw or h.value) + (f" ({h.scope})" if h.scope else "")
                for h in hps))  # fmt: skip
            cells.append(Cell(values=values[:3], pages=_pages(list(hps))))
        if any(c.values for c in cells):
            label = canon.replace("_", " ")
            rows.append(MatrixRow(group="Training", label=label, cells=cells,
                                  shared=sum(1 for c in cells if c.values) > 1))  # fmt: skip
    return rows


def _summary_rows(papers: list[PaperData]) -> list[MatrixRow]:
    def text_row(label: str, field: str) -> MatrixRow:
        cells = [Cell(values=[i.value for i in getattr(p.extraction, field)][:3],
                      pages=_pages(getattr(p.extraction, field)[:3])) for p in papers]  # fmt: skip
        return MatrixRow(group="Overview", label=label, cells=cells)

    rows = [text_row("Task", "task"), text_row("Compute", "compute"),
            text_row("Code", "code_urls")]  # fmt: skip
    rows.append(MatrixRow(group="Overview", label="Reproducibility score", cells=[
        Cell(values=[f"{p.scorecard.score:.0f}/100"]
             if p.scorecard and p.scorecard.score is not None else [])
        for p in papers]))  # fmt: skip
    rows.append(MatrixRow(group="Overview", label="Claims checked", cells=[
        Cell(values=[f"{n} {k.replace('_', ' ')}" for k, n in p.claims.counts.items()]
             if p.claims else []) for p in papers]))  # fmt: skip
    rows.append(MatrixRow(group="Overview", label="Paper vs code", cells=[
        Cell(values=[f"{n} {k.replace('_', ' ')}" for k, n in p.code.counts.items()
                     if k in ("match", "mismatch")] if p.code else [])
        for p in papers]))  # fmt: skip
    return [r for r in rows if any(c.values for c in r.cells)]


def _header_key(text: str) -> str:
    return " ".join(sorted(re.sub(r"[^a-z0-9.]+", " ", text.lower()).split()))


def _shared_results(papers: list[PaperData]) -> list[SharedResult]:
    """Columns with the same header text in 2+ papers; each paper's own best value there."""
    by_key: dict[str, list[ResultCell | None]] = {}
    labels: dict[str, str] = {}
    direction: dict[str, bool | None] = {}
    for k, p in enumerate(papers):
        for t in p.tables:
            own = [r for r in t.rows if r.is_proposed]
            for col in t.columns:
                if not col.numeric:
                    continue
                label = f"{col.group} {col.header}".strip() if col.group else col.header
                key = _header_key(label)
                if not key or not re.search(r"[a-z]", key):
                    continue
                cells = [(r, c) for r in own for c in r.cells
                         if c.col == col.index and c.value is not None]  # fmt: skip
                if not cells:
                    continue
                best = max(cells, key=lambda rc: rc[1].value or 0.0) if col.higher_is_better \
                    is not False else min(cells, key=lambda rc: rc[1].value or 0.0)  # fmt: skip
                row, cell = best
                slot = by_key.setdefault(key, [None] * len(papers))
                if slot[k] is None:
                    slot[k] = ResultCell(
                        method=row.label, text=cell.text, value=cell.value,
                        is_best=cell.is_best, table=t.label, page=t.page)  # fmt: skip
                labels.setdefault(key, label)
                direction.setdefault(key, col.higher_is_better)
    out = []
    for key, slots in by_key.items():
        if sum(1 for s in slots if s is not None) >= 2:
            out.append(SharedResult(label=labels[key], higher_is_better=direction[key],
                                    cells=[s or ResultCell() for s in slots]))  # fmt: skip
    return out


def build_comparison(papers: list[PaperData]) -> Comparison:
    comp = Comparison(papers=[
        ComparedPaper(id=p.id, title=p.extraction.metadata.title or p.title,
                      year=p.extraction.metadata.year, method=p.method)
        for p in papers])  # fmt: skip
    comp.rows = (_summary_rows(papers) + _entity_rows("Datasets", "datasets", papers)
                 + _entity_rows("Metrics", "metrics", papers) + _training_rows(papers)
                 + _entity_rows("Baselines", "baselines", papers))  # fmt: skip
    comp.results = _shared_results(papers)
    if not comp.results:
        comp.warnings.append("no results table column reads the same in two of these papers")
    return comp
