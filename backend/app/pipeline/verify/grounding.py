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


def _match_in(quote: str, block: Block) -> _Match | None:
    text = normalize(block.text if block.type != "table" else _table_text(block))
    if not text:
        return None
    if len(quote) > len(text) * 1.2:  # quote longer than the block: compare the other way
        score = fuzz.partial_ratio(text, quote)
        return _Match(block, 0, len(text), score)
    al = fuzz.partial_ratio_alignment(quote, text)
    if al is None:
        return None
    return _Match(block, al.dest_start, al.dest_end, al.score)


def _table_text(block: Block) -> str:
    grid = block.table.grid() if block.table else []
    return block.text + " " + " ".join(" ".join(r) for r in grid)


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
                match = locate(ev.quote, ev.chunk_id, blocks)
                if match is None:
                    ev.grounding_status = "unlocated"
                    ev.match_score = None
                    run.unlocated += 1
                    continue
                run.located += 1
                ev.chunk_id = match.block.id
                ev.page = match.block.page
                ev.match_score = round(match.score, 1)
                ev.boxes = span_boxes(match, pdf, ev.quote)
                ev.bbox = union_box(ev.boxes)
                if ev.boxes:
                    ev.page = ev.boxes[0].page
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
        _check_support(client, to_check[start : start + SUPPORT_BATCH], run)
    return run


def _check_support(
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
