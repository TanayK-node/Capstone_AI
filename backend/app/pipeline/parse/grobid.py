"""GROBID parser: structure, sentences, references and table locations from GROBID; table
grids rebuilt from the PDF with PyMuPDF (see tables.py)."""

from __future__ import annotations

from pathlib import Path

import httpx
import pymupdf

from app.pipeline.parse.base import ParseError
from app.pipeline.parse.tables import grid_problem, reconstruct_table
from app.pipeline.parse.tei import tei_to_document
from app.schemas.document import Block, Box, ParsedDocument, TableData

# Element types GROBID should attach coordinates to.
TEI_COORDINATES = ["title", "head", "p", "s", "figure", "formula", "biblStruct", "note"]


class GrobidParser:
    name = "grobid"

    def __init__(self, url: str, timeout_s: float = 180.0, http: httpx.Client | None = None):
        self._http = http or httpx.Client(base_url=url.rstrip("/"), timeout=timeout_s)

    def is_alive(self) -> bool:
        try:
            return self._http.get("/api/isalive", timeout=3).text.strip() == "true"
        except httpx.HTTPError:
            return False

    def version(self) -> str:
        try:
            return self._http.get("/api/version", timeout=3).text.strip() or "unknown"
        except httpx.HTTPError:
            return "unknown"

    def fulltext_tei(self, pdf: bytes) -> bytes:
        data: dict[str, str | list[str]] = {
            "consolidateHeader": "0",  # consolidation calls Crossref; keep parsing offline
            "consolidateCitations": "0",
            "includeRawCitations": "1",
            "segmentSentences": "1",
            "teiCoordinates": TEI_COORDINATES,  # repeated form field
        }
        try:
            resp = self._http.post(
                "/api/processFulltextDocument",
                files={"input": ("paper.pdf", pdf, "application/pdf")},
                data=data,
            )
        except httpx.HTTPError as exc:
            raise ParseError(f"GROBID request failed: {exc}") from exc
        if resp.status_code == 503:
            raise ParseError("GROBID is busy (503); retry later")
        if resp.status_code != 200:
            raise ParseError(f"GROBID HTTP {resp.status_code}: {resp.text[:200]}")
        return resp.content

    def parse(self, pdf_path: Path) -> ParsedDocument:
        tei = self.fulltext_tei(pdf_path.read_bytes())
        return parse_with_tei(pdf_path, tei, parser_version=self.version())


def parse_with_tei(pdf_path: Path, tei: bytes, parser_version: str = "unknown") -> ParsedDocument:
    """Two passes: locate and rebuild tables, then re-read the TEI ignoring text inside them."""
    first = tei_to_document(tei, parser_version)
    rebuilt: dict[int, tuple[Block, Box]] = {}  # index among table blocks -> (table, region)
    with pymupdf.open(pdf_path) as pdf:
        for i, block in enumerate(first.tables):
            if block.bbox is None or block.page > pdf.page_count:
                continue
            page = pdf[block.page - 1]
            b = block.bbox
            caption = block.table.caption if block.table else ""
            result = reconstruct_table(
                page, pymupdf.Rect(b.x0, b.y0, b.x1, b.y1), caption=caption, label=block.label
            )
            if result is None:
                continue
            table, used = result
            region = Box(page=block.page, x0=used.x0, y0=used.y0, x1=used.x1, y1=used.y1)
            rebuilt[i] = (block.model_copy(update={"table": table}), region)

    regions = [r for _, r in rebuilt.values()]
    doc = tei_to_document(tei, parser_version, exclude=regions)
    if regions:
        with pymupdf.open(pdf_path) as pdf:
            _strip_table_fragments(doc, regions, pdf)
    for i, block in enumerate(doc.tables):
        if i not in rebuilt:
            name = block.label or block.id
            problem = grid_problem(block.table) if block.table else "no grid"
            if problem is None:
                doc.warnings.append(f"{name}: kept GROBID's table grid")
            else:
                # A wrong grid is worse than none (claims are checked against these cells).
                caption = block.table.caption if block.table else ""
                block.table = TableData(label=block.label, caption=caption)
                doc.warnings.append(f"{name}: no reliable grid ({problem})")
            continue
        table_block, region = rebuilt[i]
        block.table = table_block.table
        # Highlight the whole table (GROBID's box often misses the header rows).
        merged = Box(
            page=region.page,
            x0=min(region.x0, block.bbox.x0) if block.bbox else region.x0,
            y0=min(region.y0, block.bbox.y0) if block.bbox else region.y0,
            x1=max(region.x1, block.bbox.x1) if block.bbox else region.x1,
            y1=max(region.y1, block.bbox.y1) if block.bbox else region.y1,
        )
        block.bbox = merged
        block.boxes = [merged]
    return doc


def _inside(box: Box, region: Box) -> bool:
    w = min(box.x1, region.x1) - max(box.x0, region.x0)
    h = min(box.y1, region.y1) - max(box.y0, region.y0)
    return box.page == region.page and w > 0 and h > 0 and w * h >= 0.6 * box.area


def _strip_table_fragments(doc: ParsedDocument, regions: list[Box], pdf: pymupdf.Document) -> None:
    """Remove table-cell text GROBID glued onto the start or end of a paragraph sentence."""
    for block in doc.blocks:
        if block.type != "paragraph":
            continue
        changed = False
        for sent in block.sentences:
            stray = [b for b in sent.boxes if any(_inside(b, r) for r in regions)]
            for box in stray:
                page = pdf[box.page - 1]
                frag = page.get_textbox(pymupdf.Rect(box.x0, box.y0, box.x1, box.y1))
                frag_words = [w.strip("-") for w in frag.split()]
                words = sent.text.split()
                # The box can catch a neighbouring line too, so match word by word.
                head = _common_prefix(words, frag_words)
                tail = _common_prefix(words[::-1], frag_words[::-1])
                if head:
                    sent.text = " ".join(words[head:])
                elif tail:
                    sent.text = " ".join(words[:-tail])
                else:
                    continue
                sent.boxes.remove(box)
                changed = True
        if changed:
            block.sentences = [s for s in block.sentences if s.text]
            block.text = " ".join(s.text for s in block.sentences)
            block.boxes = [b for b in block.boxes if not any(_inside(b, r) for r in regions)]


def _common_prefix(words: list[str], frag: list[str]) -> int:
    n = 0
    for w, f in zip(words, frag, strict=False):
        if w.strip("-") != f:
            break
        n += 1
    return n
