"""PyMuPDF-only parser: the fallback when GROBID is down, and the "PyMuPDF-only" arm of
ablation A1. Heuristic: headings from font size / boldness / numbering, captions from
"Table N" / "Figure N", tables rebuilt with tables.reconstruct_table around their captions.
"""

from __future__ import annotations

import re
from collections import Counter
from itertools import pairwise
from pathlib import Path
from typing import Any

import pymupdf

from app.pipeline.parse.tables import reconstruct_table
from app.schemas.document import (
    Block,
    BlockType,
    Box,
    DocumentMetadata,
    PageInfo,
    ParsedDocument,
    Reference,
    Sentence,
    union_box,
)

_NUMBERED = re.compile(r"^(?P<n>(?:\d+|[A-Z])(?:\.\d+)*)\.?\s+(?P<title>[A-Z].{1,80})$")
_KNOWN = re.compile(
    r"^(abstract|introduction|related work|background|method(s|ology)?|approach|experiments?|"
    r"results|discussion|limitations|conclusions?|references|bibliography|acknowledge?ments?|"
    r"appendix)\b",
    re.IGNORECASE,
)
_CAPTION = re.compile(r"^\s*(?P<kind>Table|Tab\.|Figure|Fig\.)\s*(?P<num>[A-Z]?\d+)\s*[:.|]", re.I)
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\[])")


def _reading_key(block: dict[str, Any], page_width: float) -> tuple[int, float]:
    """Column-aware order: full-width blocks and the left column first, then the right one.

    Good for the common one- and two-column layouts; a wide figure in the middle of a
    two-column page will be ordered after the left column.
    """
    x0, y0, _, _ = block["bbox"]
    # Right column = starts in the right half. Centred and full-width blocks count as left.
    return (1, y0) if x0 >= page_width / 2 - 10 else (0, y0)


def _box(page: int, r: Any) -> Box:
    x0, y0, x1, y1 = r
    return Box(page=page, x0=x0, y0=y0, x1=x1, y1=y1)


def _block_text(block: dict[str, Any]) -> tuple[str, float, bool, list[Box], int]:
    """Text, max font size, all-bold flag, line boxes for one PyMuPDF text block."""
    lines: list[str] = []
    sizes: list[float] = []
    bold = True
    boxes: list[Box] = []
    page_no: int = block["_page"]
    for line in block.get("lines", []):
        spans = [s for s in line["spans"] if s["text"].strip()]
        if not spans:
            continue
        lines.append("".join(s["text"] for s in line["spans"]).strip())
        sizes.extend(s["size"] for s in spans)
        bold = bold and all(s["flags"] & 16 or "bold" in s["font"].lower() for s in spans)
        boxes.append(_box(page_no, line["bbox"]))
    text = ""
    for ln in lines:  # de-hyphenate line breaks
        text = text[:-1] + ln if text.endswith("-") else (f"{text} {ln}" if text else ln)
    return text, max(sizes, default=0.0), bold and bool(lines), boxes, len(lines)


class PyMuPDFParser:
    name = "pymupdf"

    def parse(self, pdf_path: Path) -> ParsedDocument:
        with pymupdf.open(pdf_path) as pdf:
            return self._parse(pdf)

    def _parse(self, pdf: pymupdf.Document) -> ParsedDocument:
        pages = [
            PageInfo(number=i + 1, width=pdf[i].rect.width, height=pdf[i].rect.height)
            for i in range(pdf.page_count)
        ]
        raw: list[dict[str, Any]] = []
        for i in range(pdf.page_count):
            page = pdf[i]
            page_blocks = [b for b in page.get_text("dict")["blocks"] if b.get("type") == 0]
            for block in sorted(page_blocks, key=lambda b: _reading_key(b, page.rect.width)):
                block["_page"] = i + 1
                raw.append(block)

        # Body font size = most common size, weighted by characters.
        weights: Counter[float] = Counter()
        for block in raw:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    weights[round(span["size"], 1)] += len(span["text"].strip())
        body = weights.most_common(1)[0][0] if weights else 10.0

        # Tables first: rebuild around each "Table N" caption; their text is then skipped.
        table_blocks: list[Block] = []
        table_regions: list[Box] = []
        table_captions: set[int] = set()  # id() of raw caption blocks used by a table
        for block in raw:
            text, *_ = _block_text(block)
            m = _CAPTION.match(text)
            if not m or not m.group("kind").lower().startswith("tab"):
                continue
            page = pdf[block["_page"] - 1]
            region = self._table_region(page, pymupdf.Rect(block["bbox"]), raw, block["_page"])
            table_label = f"Table {m.group('num')}"
            result = (
                reconstruct_table(page, region, caption=text, label=table_label) if region else None
            )
            if result is None:
                continue
            table, used = result
            box = _box(block["_page"], used)
            table_regions.append(box)
            table_captions.add(id(block))
            table_blocks.append(
                Block(
                    id="",
                    type="table",
                    order=0,
                    page=block["_page"],
                    bbox=box,
                    boxes=[box],
                    text=text,
                    table=table,
                    label=table_label,
                )
            )

        blocks: list[Block] = []
        meta = DocumentMetadata()
        path: list[tuple[int, str]] = []
        in_refs = False
        references: list[Reference] = []
        ref_x0: list[float] = []  # first-line x of each reference, for hanging-indent merging
        for block in raw:
            text, size, bold, boxes, n_lines = _block_text(block)
            if not text or id(block) in table_captions or self._in_regions(boxes, table_regions):
                continue
            page_no = block["_page"]
            kind: BlockType = "paragraph"
            label: str | None = None
            short = n_lines <= 2 and len(text) <= 100 and not text.endswith(".")
            numbered = _NUMBERED.match(text)

            if page_no == 1 and meta.title is None and size >= body * 1.3 and n_lines <= 3:
                kind, meta.title = "title", text
            elif short and (size >= body * 1.12 or bold) and (numbered or _KNOWN.match(text)):
                kind = "heading"
                depth = numbered.group("n").count(".") + 1 if numbered else 1
                path = [(d, t) for d, t in path if d < depth] + [(depth, text)]
                in_refs = bool(re.match(r"^(references|bibliography)\b", text, re.I))
            elif m := _CAPTION.match(text):
                kind = "figure"
                label = f"Figure {m.group('num')}"
            elif in_refs:
                kind = "reference"
            elif n_lines <= 2 and re.search(r"\(\d+[a-z]?\)$", text) and len(text) < 160:
                kind = "equation"  # short block ending in an equation number "(3)"

            if kind == "reference":
                # Wrapped lines of a reference can arrive as their own blocks. They are indented
                # (hanging indent) relative to the reference's first line, or, in numbered
                # styles, simply lack the "[n]" marker.
                x0 = block["bbox"][0]
                prev_x0 = ref_x0[-1] if ref_x0 else None
                numbered_style = bool(references) and references[-1].text.startswith("[")
                continuation = prev_x0 is not None and (
                    (x0 > prev_x0 + 3 and abs(x0 - prev_x0) < 40)
                    or (numbered_style and not re.match(r"^\s*\[\d+\]", text))
                )
                if references and continuation:
                    prev = references[-1]
                    prev.text = f"{prev.text} {text}"
                    prev.boxes += boxes
                    blocks[-1].text, blocks[-1].boxes = prev.text, prev.boxes
                    continue
                for part in self._split_refs(text):
                    ref_x0.append(x0)
                    ref = Reference(id=f"r{len(references)}", text=part, boxes=list(boxes))
                    references.append(ref)
                    blocks.append(self._mk("reference", part, ref.boxes, [t for _, t in path]))
                continue
            # Before the first heading: front matter (authors, affiliations), no section.
            section = [t for _, t in path] if kind != "title" else []
            sentences = (
                [Sentence(text=s) for s in _SENT_SPLIT.split(text)] if kind == "paragraph" else []
            )
            blocks.append(self._mk(kind, text, boxes, section, sentences, label))

        # Insert tables in reading order (after the last block above them on their page).
        for tb in table_blocks:
            assert tb.bbox is not None
            at = 0
            for i, b in enumerate(blocks):
                if b.bbox and (b.page, b.bbox.y0) <= (tb.page, tb.bbox.y0):
                    at = i + 1
                    tb.section_path = b.section_path
            blocks.insert(at, tb)
        for i, b in enumerate(blocks):
            b.order, b.id = i, f"b{i:04d}"

        abstract = [b.text for b in blocks if b.section_path[:1] == ["Abstract"]]
        meta.abstract = " ".join(abstract) or None
        return ParsedDocument(
            parser="pymupdf",
            parser_version=pymupdf.VersionBind,
            pages=pages,
            metadata=meta,
            blocks=blocks,
            references=references,
            warnings=["parsed without GROBID: headings and references are heuristic"],
        )

    @staticmethod
    def _mk(
        kind: BlockType,
        text: str,
        boxes: list[Box],
        section: list[str],
        sentences: list[Sentence] | None = None,
        label: str | None = None,
    ) -> Block:
        bbox = union_box(boxes)
        return Block(
            id="",
            type=kind,
            order=0,
            page=bbox.page if bbox else 1,
            bbox=bbox,
            boxes=boxes,
            section_path=section,
            text=text,
            sentences=sentences or [],
            label=label,
        )

    @staticmethod
    def _in_regions(boxes: list[Box], regions: list[Box]) -> bool:
        def inside(b: Box) -> bool:
            for r in regions:
                w = min(b.x1, r.x1) - max(b.x0, r.x0)
                h = min(b.y1, r.y1) - max(b.y0, r.y0)
                if r.page == b.page and w > 0 and h > 0 and w * h >= 0.6 * b.area:
                    return True
            return False

        return bool(boxes) and all(inside(b) for b in boxes)

    @staticmethod
    def _table_region(
        page: pymupdf.Page, caption: pymupdf.Rect, raw: list[dict[str, Any]], page_no: int
    ) -> pymupdf.Rect | None:
        """Blocks right above (or, failing that, below) the caption in the same column."""

        def tabular(block: dict[str, Any]) -> bool:
            text, *_ = _block_text(block)
            digits = sum(c.isdigit() for c in text)
            words = page.get_text("words", clip=pymupdf.Rect(block["bbox"]))
            gaps = sum(1 for a, b in pairwise(words) if abs(a[1] - b[1]) < 2 and b[0] - a[2] > 5)
            return digits >= 3 and gaps >= 2

        same_col = [
            b
            for b in raw
            if b["_page"] == page_no
            and min(b["bbox"][2], caption.x1) - max(b["bbox"][0], caption.x0) > 0
        ]
        for direction in ("above", "below"):
            if direction == "above":
                cands = sorted(
                    (b for b in same_col if b["bbox"][3] <= caption.y0 + 1),
                    key=lambda b: -b["bbox"][3],
                )
            else:
                cands = sorted(
                    (b for b in same_col if b["bbox"][1] >= caption.y1 - 1),
                    key=lambda b: b["bbox"][1],
                )
            region: pymupdf.Rect | None = None
            for b in cands:
                if not tabular(b):
                    break
                region = pymupdf.Rect(b["bbox"]) if region is None else region | b["bbox"]
            if region is not None:
                return region
        return None

    @staticmethod
    def _split_refs(text: str) -> list[str]:
        """Split a block holding several numbered references ("[1] ... [2] ...")."""
        return [p.strip() for p in re.split(r"\s(?=\[\d+\]\s)", text) if p.strip()]
