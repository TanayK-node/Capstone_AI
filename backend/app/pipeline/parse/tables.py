"""Table reconstruction and normalization (M2).

GROBID is good at *finding* tables but loses structure (merged header cells, dropped rows), so
we rebuild the grid ourselves from PyMuPDF word positions inside the table region:

  1. grow the region up to the table's top rule (GROBID boxes often miss the header) and drop
     caption lines;
  2. cluster words into lines by vertical centre;
  3. find column boundaries from whitespace gaps in the numeric (data) lines;
  4. merge wrapped lines ("BERT-" / "base") into the row above;
  5. mark bold cells from the font, and parse numbers (CLAUDE.md rule 4: Python parses numbers).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from itertools import pairwise

import pymupdf

from app.schemas.document import TableCell, TableData

# ------------------------------------------------------------------ numbers

# Unicode minus, en/em/figure dashes -> ASCII hyphen-minus.
_MINUS = str.maketrans({"\u2212": "-", "\u2013": "-", "\u2014": "-", "\u2012": "-"})
_NUM = r"[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)?(?:\.\d+)?(?:[eE][-+]?\d+)?"
_NUMBER_RE = re.compile(
    rf"^\s*(?P<value>{_NUM})\s*(?P<pct>%)?\s*"
    rf"(?:(?:±|\+/-|\+-)\s*(?P<std>{_NUM})\s*%?|\(\s*±?\s*(?P<std2>{_NUM})\s*\))?"
    r"\s*%?\s*[*\u2020\u2021\u00a7\u00b6\u2217]*\s*$"  # footnote marks
)


@dataclass(frozen=True)
class ParsedNumber:
    value: float
    std: float | None = None
    is_percent: bool = False


def parse_number(text: str) -> ParsedNumber | None:
    """Parse a table cell like '24.3 ± 0.2', '84.6%', '-0.5', '1,234', '88.0*', '3e-4'."""
    t = text.translate(_MINUS).replace("\u2009", " ").strip()  # thin space
    if not t or not any(c.isdigit() for c in t):
        return None
    m = _NUMBER_RE.match(t)
    if m is None or not re.search(r"\d", m.group("value") or ""):
        return None
    try:
        value = float(m.group("value").replace(",", ""))
        raw_std = m.group("std") or m.group("std2")
        std = float(raw_std.replace(",", "")) if raw_std else None
    except ValueError:
        return None
    return ParsedNumber(value=value, std=std, is_percent="%" in t)


def normalize_table(table: TableData) -> TableData:
    """Fill numeric fields and detect header rows (leading rows with no numeric cells)."""
    rows: dict[int, list[TableCell]] = {}
    for cell in table.cells:
        num = parse_number(cell.text)
        cell.value = num.value if num else None
        cell.std = num.std if num else None
        cell.is_percent = bool(num and num.is_percent)
        rows.setdefault(cell.row, []).append(cell)

    header_rows = 0
    for r in range(table.n_rows):
        # A header row has no numbers outside the first (label) column. Years like "2019" in a
        # header are rare enough to accept the error.
        if any(c.value is not None for c in rows.get(r, []) if c.col > 0):
            break
        header_rows += 1
    if header_rows == table.n_rows:  # no numeric rows at all: treat only row 0 as header
        header_rows = min(1, table.n_rows)
    table.header_rows = header_rows
    for cell in table.cells:
        cell.is_header = cell.row < header_rows
    return table


# ------------------------------------------------------------------ reconstruction

_CAPTION_RE = re.compile(r"^\s*(Table|Tab\.|TABLE)\s*[A-Z]?\d+", re.IGNORECASE)
MIN_COL_GAP = 5.0  # points; inter-word spaces are ~2-3 pt, LaTeX tabcolsep gives ~12 pt


@dataclass
class _Word:
    x0: float
    y0: float
    x1: float
    y1: float
    text: str
    bold: bool = False

    @property
    def yc(self) -> float:
        return (self.y0 + self.y1) / 2


@dataclass
class _Line:
    words: list[_Word] = field(default_factory=list)

    @property
    def y0(self) -> float:
        return min(w.y0 for w in self.words)

    @property
    def y1(self) -> float:
        return max(w.y1 for w in self.words)

    @property
    def text(self) -> str:
        return " ".join(w.text for w in self.words)

    def groups(self, min_gap: float = MIN_COL_GAP) -> int:
        ws = sorted(self.words, key=lambda w: w.x0)
        return 1 + sum(1 for a, b in pairwise(ws) if b.x0 - a.x1 >= min_gap)

    def has_number(self) -> bool:
        return any(parse_number(w.text) is not None for w in self.words)


def _bold_rects(page: pymupdf.Page, clip: pymupdf.Rect) -> list[pymupdf.Rect]:
    rects: list[pymupdf.Rect] = []
    for block in page.get_text("dict", clip=clip)["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                font = span["font"].lower()
                # flags bit 4 = bold; LaTeX bold fonts are CMBX / *-Bold / *Medium.
                if span["flags"] & 16 or "bold" in font or "cmbx" in font or "medi" in font:
                    rects.append(pymupdf.Rect(span["bbox"]))
    return rects


def _words(page: pymupdf.Page, clip: pymupdf.Rect) -> list[_Word]:
    bold = _bold_rects(page, clip)
    out: list[_Word] = []
    for x0, y0, x1, y1, text, *_ in page.get_text("words", clip=clip):
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        is_bold = any(r.contains(pymupdf.Point(cx, cy)) for r in bold)
        out.append(_Word(x0, y0, x1, y1, text, is_bold))
    return out


def _cluster_lines(words: list[_Word]) -> list[_Line]:
    lines: list[_Line] = []
    for w in sorted(words, key=lambda w: w.yc):
        if lines:
            last = lines[-1]
            height = last.y1 - last.y0
            if abs(w.yc - sum(x.yc for x in last.words) / len(last.words)) < 0.35 * height:
                last.words.append(w)
                continue
        lines.append(_Line([w]))
    for line in lines:
        line.words.sort(key=lambda w: w.x0)
    return lines


def _top_rule(page: pymupdf.Page, region: pymupdf.Rect, reach: float = 60.0) -> float | None:
    """Top of the table's ruling just above the region, or None.

    Walks upward through drawings that sit inside the region's x-span: cell borders of ruled
    tables chain together (gap <= 3 pt), and a wide booktabs \\toprule may sit one header
    line above the region (gap <= 20 pt).
    """
    cands: list[pymupdf.Rect] = []
    for drawing in page.get_drawings():
        r = pymupdf.Rect(drawing["rect"])
        inside_x = r.x0 >= region.x0 - 15 and r.x1 <= region.x1 + 15
        if inside_x and region.y0 - reach <= r.y0 <= region.y1:
            cands.append(r)
    top = region.y0
    changed = True
    while changed:
        changed = False
        for r in cands:
            max_gap = 20.0 if r.width >= 0.5 * region.width else 3.0
            if r.y0 < top - 0.5 and r.y1 >= top - max_gap:
                top = r.y0
                changed = True
    return top if top < region.y0 - 0.5 else None


def _column_spans(lines: list[_Line]) -> list[tuple[float, float]]:
    """Merge word x-intervals of data lines; gaps >= MIN_COL_GAP separate columns."""
    data = [ln for ln in lines if ln.has_number()] or lines
    intervals = sorted((w.x0, w.x1) for ln in data for w in ln.words)
    spans: list[list[float]] = []
    for x0, x1 in intervals:
        if spans and x0 - spans[-1][1] < MIN_COL_GAP:
            spans[-1][1] = max(spans[-1][1], x1)
        else:
            spans.append([x0, x1])
    return [(a, b) for a, b in spans]


def _assign_col(word: _Word, spans: list[tuple[float, float]]) -> int:
    def overlap(span: tuple[float, float]) -> float:
        return min(word.x1, span[1]) - max(word.x0, span[0])

    best = max(range(len(spans)), key=lambda i: overlap(spans[i]))
    if overlap(spans[best]) > 0:
        return best
    xc = (word.x0 + word.x1) / 2  # header word over a gap: nearest column centre
    return min(range(len(spans)), key=lambda i: abs((spans[i][0] + spans[i][1]) / 2 - xc))


def _join(a: str, b: str) -> str:
    if not a:
        return b
    if not b:
        return a
    return a + b if a.endswith("-") else f"{a} {b}"


def reconstruct_table(
    page: pymupdf.Page, region: pymupdf.Rect, caption: str = "", label: str | None = None
) -> tuple[TableData, pymupdf.Rect] | None:
    """Rebuild a table grid from word positions.

    Returns the table and the region its rows actually occupy (header included, caption
    excluded), or None if no plausible grid is found.
    """
    region = pymupdf.Rect(region) & page.rect
    top = _top_rule(page, region)
    clip = pymupdf.Rect(
        region.x0 - 4, (top if top is not None else region.y0) - 1, region.x1 + 4, region.y1 + 1
    )
    lines = _cluster_lines(_words(page, clip))

    # Drop the caption and its continuation lines (single-group lines right after it).
    keep: list[_Line] = []
    in_caption = False
    for line in lines:
        if _CAPTION_RE.match(line.text):
            in_caption = True
            continue
        if in_caption and line.groups() <= 1 and not line.has_number():
            continue
        in_caption = False
        keep.append(line)
    lines = keep
    if len(lines) < 2:
        return None

    spans = _column_spans(lines)
    if len(spans) < 2:
        return None

    used = pymupdf.Rect(
        min(w.x0 for ln in lines for w in ln.words),
        lines[0].y0,
        max(w.x1 for ln in lines for w in ln.words),
        lines[-1].y1,
    )
    rows: list[list[str]] = []
    bold: list[list[bool]] = []
    prev: _Line | None = None
    for line in lines:
        cells = ["" for _ in spans]
        cell_bold = [False for _ in spans]
        for w in line.words:
            c = _assign_col(w, spans)
            cells[c] = _join(cells[c], w.text)
            cell_bold[c] = cell_bold[c] or w.bold
        filled = sum(1 for c in cells if c)
        # Wrapped line: no numbers, fills under half the columns, and sits tight under the
        # previous line. Merge it into the previous row instead of starting a new one.
        wrapped = (
            prev is not None
            and rows
            and not line.has_number()
            and filled < max(2, len(spans) / 2)
            and line.y0 - prev.y1 < 0.6 * (line.y1 - line.y0)
        )
        if wrapped:
            rows[-1] = [_join(a, b) for a, b in zip(rows[-1], cells, strict=True)]
            bold[-1] = [a or b for a, b in zip(bold[-1], cell_bold, strict=True)]
        else:
            rows.append(cells)
            bold.append(cell_bold)
        prev = line

    table = TableData(
        label=label,
        caption=caption,
        n_rows=len(rows),
        n_cols=len(spans),
        cells=[
            TableCell(text=text, row=r, col=c, is_bold=bold[r][c])
            for r, row in enumerate(rows)
            for c, text in enumerate(row)
        ],
    )
    return normalize_table(table), used


def table_from_rows(
    rows: list[list[str]], caption: str = "", label: str | None = None
) -> TableData:
    """Build a TableData from a plain row list (GROBID's own grid, used as a fallback)."""
    n_cols = max((len(r) for r in rows), default=0)
    table = TableData(
        label=label,
        caption=caption,
        n_rows=len(rows),
        n_cols=n_cols,
        cells=[
            TableCell(text=text, row=r, col=c)
            for r, row in enumerate(rows)
            for c, text in enumerate(row)
        ],
    )
    return normalize_table(table)
