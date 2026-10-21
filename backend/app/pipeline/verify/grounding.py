"""Grounding verifier (M5): is each quote really in the paper, where, and does it support
the extracted value?

1. Locate the quote in the parsed text with fuzzy matching (rapidfuzz), first in the cited
   block, then anywhere in the paper (models sometimes cite the wrong paragraph).
2. Map the matched span to sentence boxes (GROBID gives per-sentence coordinates); without
   sentence boxes, search the PDF page for the quote.
3. Ask a small model, in one batched call, whether each located quote supports its value.

Items are never dropped: failures become "unlocated" / "unsupported" badges (CLAUDE.md rule 5).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf
from rapidfuzz import fuzz

from app import prompts
from app.llm.client import LLMClient
from app.llm.errors import LLMError
from app.schemas.document import Block, Box, ParsedDocument, union_box
from app.schemas.extraction import Evidence, PaperExtraction, SupportOut

log = logging.getLogger("paperlens.verify")

MATCH_THRESHOLD = 90.0  # rapidfuzz partial ratio, 0-100
SEARCHABLE = {"paragraph", "table", "caption", "footnote", "equation", "figure", "title"}
SUPPORT_BATCH = 40
_STATUS = {"yes": "verified", "partial": "partial", "no": "unsupported"}


@dataclass
class VerifyRun:
    located: int = 0
    unlocated: int = 0
    checked: int = 0
    support_calls: int = 0
    prompt_version: str | None = None
    provider: str | None = None
    model: str | None = None
    warnings: list[str] = field(default_factory=list)


def normalize(text: str) -> str:
    """Comparable text: unify quotes/dashes/ligatures, undo hyphenation, collapse space."""
    t = (
        text.replace("ﬁ", "fi")
        .replace("ﬂ", "fl")
        .replace("’", "'")
        .replace("‘", "'")
        .replace("“", '"')
        .replace("”", '"')
        .replace("–", "-")
        .replace("—", "-")
        .replace("−", "-")
    )
    t = re.sub(r"(\w)- (\w)", r"\1\2", t)  # "repre- sentation"
    return re.sub(r"\s+", " ", t).strip()


@dataclass
class _Match:
    block: Block
    start: int
    end: int
    score: float


def _table_rows(block: Block) -> list[str]:
    """Caption, then one line per grid row with cells joined by " | " exactly as the
    extraction prompt shows tables (extract/groups.render_block), so a quoted row matches."""
    grid = block.table.grid() if block.table else []
    return [normalize(block.text), *(normalize(" | ".join(r)) for r in grid)]


def _match_in(quote: str, block: Block) -> _Match | None:
    text = " ".join(_table_rows(block)) if block.type == "table" else normalize(block.text)
    if not text:
        return None
    if len(quote) > len(text) * 1.2:  # quote longer than the block: compare the other way
        score = fuzz.partial_ratio(text, quote)
        return _Match(block, 0, len(text), score)
    al = fuzz.partial_ratio_alignment(quote, text)
    if al is None:
        return None
    return _Match(block, al.dest_start, al.dest_end, al.score)


def locate(quote: str, cited: str, blocks: dict[str, Block]) -> _Match | None:
    q = normalize(quote)
    if len(q) < 8:
        return None
    best: _Match | None = None
    if cited in blocks:
        best = _match_in(q, blocks[cited])
        if best and best.score >= MATCH_THRESHOLD:
            return best
    for block in blocks.values():
        if block.id == cited or block.type not in SEARCHABLE:
            continue
        m = _match_in(q, block)
        if m and (best is None or m.score > best.score):
            best = m
    return best if best and best.score >= MATCH_THRESHOLD else None


def span_boxes(match: _Match, pdf: pymupdf.Document | None, quote: str) -> list[Box]:
    """Boxes of the sentences the matched span covers; PDF text search as a fallback."""
    block = match.block
    if block.type == "table" and pdf is not None:
        rows = _row_boxes(match, pdf)
        if rows:
            return rows
    if block.sentences and any(s.boxes for s in block.sentences):
        boxes: list[Box] = []
        pos = 0
        for sentence in block.sentences:
            text = normalize(sentence.text)
            start, end = pos, pos + len(text)
            pos = end + 1  # sentences are joined with one space in block.text
            if end > match.start and start < match.end:
                boxes += sentence.boxes
        if boxes:
            return boxes
    if pdf is not None and 1 <= block.page <= pdf.page_count:
        words = quote.split()
        page = pdf[block.page - 1]
        for n in (12, 8, 5):  # shorter snippets survive line breaks and hyphenation better
            snippet = " ".join(words[:n])
            if len(snippet) < 12:
                break
            hits = page.search_for(snippet)
            if hits:
                return [Box(page=block.page, x0=r.x0, y0=r.y0, x1=r.x1, y1=r.y1) for r in hits]
    return list(block.boxes)


def _row_boxes(match: _Match, pdf: pymupdf.Document) -> list[Box]:
    """Boxes of the grid rows a table quote covers: the row's first cell is searched inside
    the table's box on the page, and the hit's line spans the table's width. The caption
    (piece 0) and rows that cannot be found fall back to the whole table (caller)."""
    block = match.block
    if block.bbox is None or not block.table or not 1 <= block.bbox.page <= pdf.page_count:
        return []
    table = block.bbox
    page = pdf[table.page - 1]
    clip = pymupdf.Rect(table.x0 - 2, table.y0 - 2, table.x1 + 2, table.y1 + 2)
    grid = block.table.grid()
    boxes: list[Box] = []
    pos = 0
    for i, piece in enumerate(_table_rows(block)):
        start, end = pos, pos + len(piece)
        pos = end + 1
        if i == 0 or not (end > match.start and start < match.end):
            continue
        row = grid[i - 1]
        cells = [c for c in row if c.strip()]
        if not cells:
            continue
        hits = [h for h in _line_hits(page, cells[0], clip) if _row_on_line(page, h, cells, clip)]
        # The same first cell can repeat ("MoCo" twice): take the hit matching its rank.
        rank = sum(1 for r in grid[: i - 1] if next((c for c in r if c.strip()), "") == cells[0])
        if hits:
            hit = hits[min(rank, len(hits) - 1)]
            boxes.append(
                Box(page=table.page, x0=table.x0, y0=hit.y0 - 1, x1=table.x1, y1=hit.y1 + 1)
            )
    return boxes


def _line_hits(page: pymupdf.Page, text: str, clip: pymupdf.Rect) -> list[pymupdf.Rect]:
    # PDF text search can return a few-point-wide "hit" on an unrelated glyph; a real
    # match is at least ~1.5 pt per character wide.
    hits = [h for h in page.search_for(text, clip=clip) if h.width >= 1.5 * len(text.strip())]
    return sorted(hits, key=lambda r: (r.y0, r.x0))


def _row_on_line(
    page: pymupdf.Page, hit: pymupdf.Rect, cells: list[str], clip: pymupdf.Rect
) -> bool:
    """Is another cell of the row also on this line? Guards against a first cell ("24",
    "ResNet-50") that occurs in many rows."""
    if len(cells) < 2:
        return True
    line = pymupdf.Rect(clip.x0, hit.y0 - 2, clip.x1, hit.y1 + 2)
    return any(page.search_for(c, clip=line) for c in cells[1:3])


def attach_location(ev: Evidence, blocks: dict[str, Block], pdf: pymupdf.Document | None) -> bool:
    """Find the quote in the paper and fill chunk_id / page / boxes. False = not found,
    and the evidence is marked "unlocated" (kept, never dropped)."""
    match = locate(ev.quote, ev.chunk_id, blocks)
    if match is None:
        ev.grounding_status = "unlocated"
        ev.match_score = None
        return False
    ev.chunk_id = match.block.id
    ev.page = match.block.page
    ev.match_score = round(match.score, 1)
    ev.boxes = span_boxes(match, pdf, ev.quote)
    ev.bbox = union_box(ev.boxes)
    if ev.boxes:
        ev.page = ev.boxes[0].page
    return True


def ground(
    extraction: PaperExtraction,
    doc: ParsedDocument,
    client: LLMClient | None,
    pdf_path: Path | None = None,
) -> VerifyRun:
    run = VerifyRun()
    blocks = {b.id: b for b in doc.blocks}
    pdf = pymupdf.open(pdf_path) if pdf_path and pdf_path.exists() else None
    try:
        to_check: list[tuple[str, str, Evidence]] = []  # (field, value, evidence)
        for name, item in extraction.all_items():
            for ev in item.evidence:
                if not attach_location(ev, blocks, pdf):
                    run.unlocated += 1
                    continue
                run.located += 1
                if item.source == "rule":
                    ev.grounding_status = "verified"  # a regex hit is its own evidence
                else:
                    ev.grounding_status = "unchecked"
                    to_check.append((name, item.value, ev))
    finally:
        if pdf is not None:
            pdf.close()

    if client is None:
        if to_check:
            run.warnings.append("no LLM available: support of located quotes not checked")
        return run
    for start in range(0, len(to_check), SUPPORT_BATCH):
        check_support(client, to_check[start : start + SUPPORT_BATCH], run)
    return run


def check_support(
    client: LLMClient, batch: list[tuple[str, str, Evidence]], run: VerifyRun
) -> None:
    prompt = prompts.render(
        "verify_support",
        items=[
            {"id": i, "field": f, "value": v, "quote": ev.quote[:500]}
            for i, (f, v, ev) in enumerate(batch)
        ],
    )
    run.prompt_version = prompt.id
    try:
        result = client.generate_json(prompt, SupportOut, role="small")
    except LLMError as exc:
        run.warnings.append(f"support check failed: {type(exc).__name__}: {exc}")
        return
    run.support_calls += 0 if result.meta.cached else 1
    run.provider, run.model = result.meta.provider, result.meta.model
    for verdict in result.value.verdicts:
        if 0 <= verdict.id < len(batch):
            batch[verdict.id][2].grounding_status = _STATUS[verdict.verdict]  # type: ignore[assignment]
            run.checked += 1


def grounding_score(extraction: PaperExtraction) -> float:
    """Share of items with at least one verified or partially supporting quote."""
    items = [item for _, item in extraction.all_items()]
    if not items:
        return 0.0
    good = sum(
        1
        for item in items
        if any(e.grounding_status in ("verified", "partial") for e in item.evidence)
    )
    return round(good / len(items), 3)
