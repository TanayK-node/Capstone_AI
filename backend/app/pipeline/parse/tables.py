"""Table reconstruction and normalization (M2).

GROBID is good at *finding* tables but loses structure (merged header cells, dropped rows), so
we rebuild each grid from PyMuPDF word positions; see the step list above reconstruct_table.
Numbers are parsed here, in Python (CLAUDE.md rule 4).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from itertools import pairwise
from typing import Any

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


_SCI_RE = re.compile(
    rf"^\s*(?P<mant>{_NUM})\s*(?:\u00b7|\u00d7|x|\*)\s*10\^(?P<exp>[-+]?\d+)\s*[*\u2020\u2021]*\s*$"
)


def parse_number(text: str) -> ParsedNumber | None:
    """Parse a table cell like '24.3 ± 0.2', '84.6%', '-0.5', '1,234', '88.0*', '3e-4',
    or '2.3 · 10^19' (superscripts are written with ^ by the table extractor)."""
    t = text.translate(_MINUS).replace("\u2009", " ").strip()  # thin space
    if not t or not any(c.isdigit() for c in t):
        return None
    if sci := _SCI_RE.match(t):
        try:
            return ParsedNumber(value=float(sci.group("mant")) * 10 ** int(sci.group("exp")))
        except ValueError:
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
#
# Steps, for one table whose rough region comes from GROBID (or the PyMuPDF parser):
#   1. pick the text column: on two-column pages a table lives in one column unless its own
#      caption spans the page; reading only that column keeps the other column's prose out;
#   2. read whole words (with font size, boldness) from the column around the region, cluster
#      them into lines, and mark superscripts ("10^20");
#   3. classify lines (own caption, other caption, caption continuation, prose, row) and cut
#      the lines into segments at captions, prose and large vertical gaps;
#   4. choose the segment next to the table's own caption (or overlapping the region);
#   5. find columns from whitespace aligned across most data rows (a few spanning cells can't
#      merge columns), assign cells, merge wrapped lines, detect bold;
#   6. reject the result if it looks like prose (grid_problem); no grid beats a wrong grid.

_TABLE_CAPTION_RE = re.compile(
    r"^\s*(?:Table|Tab\.|TABLE)\s*(?P<num>[A-Z]?\.?\d+(?:\.\d+)?)\s*[:.|]?", re.IGNORECASE
)
_FIGURE_CAPTION_RE = re.compile(r"^\s*(?:Figure|Fig\.|FIGURE)\s*[A-Z]?\.?\d+", re.IGNORECASE)
MIN_COL_GAP = 4.0  # points; inter-word spaces are ~2-3 pt, LaTeX tabcolsep gives ~12 pt
NUM_COL_GAP = 1.0  # two numbers side by side are separate cells even when tightly packed
PROSE_GAP = 8.0  # justified prose stretches spaces, but not this far
_DASHES = {"-", "–", "—", "−"}  # "-" cells are empty values, still a column
_OPERATORS = {"·", "×", "x", "±", "/", "+", "="}


@dataclass
class _Word:
    x0: float
    y0: float
    x1: float
    y1: float
    text: str
    bold: bool = False
    size: float = 0.0

    @property
    def yc(self) -> float:
        return (self.y0 + self.y1) / 2

    @property
    def h(self) -> float:
        return self.y1 - self.y0


def _is_num(text: str) -> bool:
    return text in _DASHES or parse_number(text) is not None


@dataclass
class _Line:
    words: list[_Word] = field(default_factory=list)
    kind: str = "row"  # row | prose | caption_own | caption_other | caption_cont

    @property
    def y0(self) -> float:
        return min(w.y0 for w in self.words)

    @property
    def y1(self) -> float:
        return max(w.y1 for w in self.words)

    @property
    def x0(self) -> float:
        return min(w.x0 for w in self.words)

    @property
    def x1(self) -> float:
        return max(w.x1 for w in self.words)

    @property
    def text(self) -> str:
        return " ".join(w.text for w in self.words)

    def groups(self, min_gap: float = MIN_COL_GAP) -> int:
        return 1 + sum(1 for a, b in pairwise(self.words) if b.x0 - a.x1 >= min_gap)

    @property
    def size(self) -> float:
        sizes = sorted(w.size for w in self.words)
        return sizes[len(sizes) // 2]

    @property
    def n_numeric(self) -> int:
        return sum(1 for w in self.words if _is_num(w.text))

    def has_number(self) -> bool:
        return any(parse_number(w.text) is not None for w in self.words)

    def is_data(self) -> bool:
        return self.n_numeric >= 2 or (self.n_numeric >= 1 and self.groups() >= 2)


def _cut(a: _Word, b: _Word) -> bool:
    """Is there a cell boundary between adjacent words a and b of one line?"""
    gap = b.x0 - a.x1
    if gap >= MIN_COL_GAP:
        return True
    if gap >= NUM_COL_GAP and _is_num(a.text) and _is_num(b.text):
        return True
    # "label 84.6" with a tight gap; but not "1.0 · 10^20" or "24.3 ± 0.2".
    return gap >= 3.0 and _is_num(b.text) and a.text not in _OPERATORS and b.text not in _DASHES


def _cells(line: _Line) -> list[list[_Word]]:
    cells: list[list[_Word]] = []
    for w in line.words:
        if cells and not _cut(cells[-1][-1], w):
            cells[-1].append(w)
        else:
            cells.append([w])
    return cells


def _join_words(words: list[_Word]) -> str:
    text = ""
    for w in words:
        if not text:
            text = w.text
        elif text.endswith("-") and w.text[:1].islower():
            text += w.text  # de-hyphenate "multi-" / "crop"
        else:
            text += " " + w.text
    return text


# ---- step 1: which text column


def _page_lines(
    page: pymupdf.Page, clip: pymupdf.Rect | None = None
) -> list[tuple[pymupdf.Rect, str]]:
    out: list[tuple[pymupdf.Rect, str]] = []
    for block in page.get_text("dict", clip=clip)["blocks"]:
        for line in block.get("lines", []):
            text = "".join(s["text"] for s in line["spans"]).strip()
            if text:
                out.append((pymupdf.Rect(line["bbox"]), text))
    return out


def _is_two_column(page: pymupdf.Page) -> bool:
    width = page.rect.width
    long_lines = [r for r, t in _page_lines(page) if len(t) > 30]
    if len(long_lines) < 10:
        return False
    narrow = sum(1 for r in long_lines if r.width < 0.5 * width)
    return narrow > 0.5 * len(long_lines)


def _caption_number(label: str | None) -> str | None:
    if not label:
        return None
    m = re.search(r"([A-Z]?\.?\d+(?:\.\d+)?)\s*$", label)
    return m.group(1).lstrip(".") if m else None


def _find_own_caption(
    page: pymupdf.Page, number: str | None, region: pymupdf.Rect
) -> pymupdf.Rect | None:
    """The caption line "Table <number>..." closest to the region (within 200 pt)."""
    if number is None:
        return None
    best: tuple[float, pymupdf.Rect] | None = None
    for rect, text in _page_lines(page):
        m = _TABLE_CAPTION_RE.match(text)
        if not m or m.group("num").replace(".", "") != number.replace(".", ""):
            continue
        dist = max(0.0, region.y0 - rect.y1, rect.y0 - region.y1)
        if dist <= 200 and (best is None or dist < best[0]):
            best = (dist, rect)
    return best[1] if best else None


def _column_bounds(
    page: pymupdf.Page, region: pymupdf.Rect, caption: pymupdf.Rect | None
) -> tuple[float, float]:
    width = page.rect.width
    if not _is_two_column(page):
        return 0.0, width
    mid = width / 2
    anchor = caption if caption is not None else region
    if anchor.width > 0.55 * width:  # full-width table (or caption) on a two-column page
        return 0.0, width
    centre = (anchor.x0 + anchor.x1) / 2
    return (0.0, mid + 4) if centre < mid else (mid - 4, width)


# ---- step 2: words and lines


def _make_word(chars: list[dict[str, Any]], bold: bool, size: float) -> _Word:
    return _Word(
        min(c["bbox"][0] for c in chars),
        min(c["bbox"][1] for c in chars),
        max(c["bbox"][2] for c in chars),
        max(c["bbox"][3] for c in chars),
        "".join(c["c"] for c in chars),
        bold,
        size,
    )


def _words(page: pymupdf.Page, clip: pymupdf.Rect) -> list[_Word]:
    """Whole words from rawdict characters, keeping font size and boldness."""
    words: list[_Word] = []
    for block in page.get_text("rawdict", clip=clip)["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                font = span["font"].lower()
                bold = bool(span["flags"] & 16) or any(k in font for k in ("bold", "cmbx", "medi"))
                size = float(span["size"])
                current: list[dict[str, Any]] = []
                for ch in span["chars"]:
                    # Break at spaces, and at gaps where the PDF positions words without one.
                    gap_break = current and ch["bbox"][0] - current[-1]["bbox"][2] > 0.3 * size
                    if ch["c"].isspace() or gap_break:
                        if current:
                            words.append(_make_word(current, bold, size))
                        current = []
                    if not ch["c"].isspace():
                        current.append(ch)
                if current:
                    words.append(_make_word(current, bold, size))
    return words


def _cluster_lines(words: list[_Word]) -> list[_Line]:
    lines: list[_Line] = []
    for w in sorted(words, key=lambda w: w.yc):
        best: _Line | None = None
        best_overlap = 0.0
        for line in lines[-4:]:
            overlap = min(w.y1, line.y1) - max(w.y0, line.y0)
            need = 0.4 * min(w.h, line.y1 - line.y0)
            if overlap >= need and overlap > best_overlap:
                best, best_overlap = line, overlap
        if best is None:
            lines.append(_Line([w]))
        else:
            best.words.append(w)
    for line in lines:
        line.words.sort(key=lambda w: w.x0)
        _merge_scripts(line)
    return sorted(lines, key=lambda ln: ln.y0)


def _merge_scripts(line: _Line) -> None:
    """Attach superscripts ("10" + "20" -> "10^20") and subscripts / split spans to the word
    they belong to."""
    merged: list[_Word] = []
    for w in line.words:
        prev = merged[-1] if merged else None
        if prev is not None and w.x0 - prev.x1 < 1.0:
            smaller = w.size < 0.85 * prev.size
            if smaller and w.yc < prev.yc - 0.15 * prev.h:
                joiner = "^"
            elif smaller or w.x0 - prev.x1 < 0.3:
                joiner = ""
            else:
                merged.append(w)
                continue
            merged[-1] = _Word(
                prev.x0,
                min(prev.y0, w.y0),
                max(prev.x1, w.x1),
                max(prev.y1, w.y1),
                prev.text + joiner + w.text,
                prev.bold or w.bold,
                prev.size,
            )
        else:
            merged.append(w)
    line.words = merged


# ---- steps 3-4: classify, segment, choose


def _classify(lines: list[_Line], number: str | None, col_width: float) -> None:
    prev: _Line | None = None
    for line in lines:
        text = line.text
        m = _TABLE_CAPTION_RE.match(text)
        if m:
            own = number is not None and m.group("num").replace(".", "") == number.replace(".", "")
            line.kind = "caption_own" if own else "caption_other"
        elif _FIGURE_CAPTION_RE.match(text):
            line.kind = "caption_other"
        elif (
            prev is not None
            and prev.kind.startswith("caption")
            and line.groups(PROSE_GAP) == 1
            and line.n_numeric <= 1
            and abs(line.size - prev.size) < 0.5
            and line.y0 - prev.y1 < 0.35 * (line.y1 - line.y0)
        ):
            line.kind = "caption_cont"  # wrapped caption text: same size, tightly spaced
        elif (
            len(line.words) >= 7
            and line.groups(PROSE_GAP) == 1
            and line.n_numeric <= 1
            and line.x1 - line.x0 >= 0.5 * col_width
        ):
            line.kind = "prose"
        prev = line


def _segments(lines: list[_Line]) -> list[list[_Line]]:
    heights = sorted(ln.y1 - ln.y0 for ln in lines) or [10.0]
    max_gap = 1.5 * heights[len(heights) // 2]
    segs: list[list[_Line]] = []
    current: list[_Line] = []
    for line in lines:
        if line.kind != "row":
            if current:
                segs.append(current)
            current = []
            continue
        if current and line.y0 - current[-1].y1 > max_gap:
            segs.append(current)
            current = []
        current.append(line)
    if current:
        segs.append(current)
    return segs


def _choose_segment(
    lines: list[_Line], segs: list[list[_Line]], region: pymupdf.Rect
) -> list[_Line] | None:
    def data_lines(seg: list[_Line]) -> int:
        return sum(1 for ln in seg if ln.is_data())

    def overlap(seg: list[_Line]) -> float:
        return max(0.0, min(seg[-1].y1, region.y1) - max(seg[0].y0, region.y0))

    index = {id(ln): i for i, ln in enumerate(lines)}
    seg_of = {id(ln): seg for seg in segs for ln in seg}
    own = [i for i, ln in enumerate(lines) if ln.kind == "caption_own"]
    if own:
        start = own[0]
        end = start
        while end + 1 < len(lines) and lines[end + 1].kind == "caption_cont":
            end += 1
        above = seg_of.get(id(lines[start - 1])) if start > 0 else None
        below = seg_of.get(id(lines[end + 1])) if end + 1 < len(lines) else None
        cands = [s for s in (above, below) if s is not None and data_lines(s) > 0]
        if len(cands) == 2 and above is not None and below is not None:
            # Caption convention: a segment that sits against another table's caption on its
            # far side belongs to that table.
            before_above = index[id(above[0])] - 1
            after_below = index[id(below[-1])] + 1
            if before_above >= 0 and lines[before_above].kind == "caption_other":
                return below
            if after_below < len(lines) and lines[after_below].kind == "caption_other":
                return above
            return max(cands, key=lambda s: (data_lines(s), overlap(s)))
        if cands:
            return cands[0]
    best = max(segs, key=lambda s: (overlap(s) > 0, data_lines(s) > 0, overlap(s)), default=None)
    if best is None or overlap(best) <= 0 or data_lines(best) == 0:
        return None
    return best


def _horizontal_rules(page: pymupdf.Page, clip: pymupdf.Rect) -> list[pymupdf.Rect]:
    rules: list[pymupdf.Rect] = []
    for drawing in page.get_drawings():
        r = pymupdf.Rect(drawing["rect"])
        if r.height <= 2.0 and r.width >= 20 and r.intersects(clip):
            rules.append(r)
    return rules


def _trim_leading_text(seg: list[_Line], rules: list[pymupdf.Rect]) -> list[_Line]:
    """Drop body-text lines glued onto the top of the table (e.g. a paragraph's last line).

    A leading line goes if it has no numbers and no column structure, and either sits above
    the table's top rule, or reads like a sentence fragment.
    """
    first_data = next((i for i, ln in enumerate(seg) if ln.is_data()), None)
    if first_data is None:
        return seg
    width = max(ln.x1 for ln in seg) - min(ln.x0 for ln in seg)
    top_rules = [
        r.y0
        for r in rules
        if r.width >= 0.4 * width and seg[0].y0 - 3 <= r.y0 <= seg[first_data].y0
    ]
    top = min(top_rules) if top_rules else None
    start = 0
    while start < first_data:
        line = seg[start]
        plain = not line.has_number() and line.groups() == 1
        above_rule = top is not None and line.y1 <= top + 1
        sentence = len(line.words) >= 4 and line.text.rstrip()[-1:] in ".,;"
        if plain and (above_rule or sentence):
            start += 1
        else:
            break
    return seg[start:]


# ---- step 5: columns


def _column_spans(seg: list[_Line]) -> list[tuple[float, float]]:
    data = [ln for ln in seg if ln.is_data()]
    if len(data) < 2:
        data = [ln for ln in seg if ln.groups() >= 2] or seg
    cell_spans = [[(c[0].x0, c[-1].x1) for c in _cells(ln)] for ln in data]
    x_min = min(a for line_spans in cell_spans for a, _ in line_spans)
    x_max = max(b for line_spans in cell_spans for _, b in line_spans)
    step = 0.25
    n = int((x_max - x_min) / step) + 2
    cover = [0] * n
    for line_spans in cell_spans:
        for a, b in line_spans:
            for i in range(int((a - x_min) / step), int((b - x_min) / step) + 1):
                cover[i] += 1
    # Blocks: separated by positions no data cell covers.
    blocks: list[tuple[int, int]] = []
    i = 0
    while i < n:
        if cover[i] == 0:
            i += 1
            continue
        j = i
        while j + 1 < n and cover[j + 1] > 0:
            j += 1
        blocks.append((i, j))
        i = j + 1
    # Inside a block, split at weak points: positions few lines cover, flanked by columns most
    # lines cover (one long cell bridging two real columns).
    tol = max(1, int(0.2 * len(data)))
    dense = max(2, int(0.5 * len(data)))
    spans: list[tuple[float, float]] = []
    for a, b in blocks:
        cuts: list[int] = []
        k = a
        while k <= b:
            if cover[k] <= tol:
                m = k
                while m + 1 <= b and cover[m + 1] <= tol:
                    m += 1
                left = max(cover[a:k], default=0)
                right = max(cover[m + 1 : b + 1], default=0)
                if left >= dense and right >= dense:
                    cuts.append((k + m) // 2)
                k = m + 1
            else:
                k += 1
        edges = [a, *cuts, b]
        for lo, hi in pairwise(edges):
            spans.append((x_min + lo * step, x_min + hi * step))
    return spans


def _assign(x0: float, x1: float, spans: list[tuple[float, float]]) -> int:
    def ov(span: tuple[float, float]) -> float:
        return min(x1, span[1]) - max(x0, span[0])

    best = max(range(len(spans)), key=lambda i: ov(spans[i]))
    if ov(spans[best]) > 0:
        return best
    xc = (x0 + x1) / 2
    return min(range(len(spans)), key=lambda i: abs((spans[i][0] + spans[i][1]) / 2 - xc))


def _is_label_line(line: _Line, spans: list[tuple[float, float]]) -> bool:
    """Section label row ("Methods using other architectures:"): text from column 0 on."""
    return (
        not line.has_number() and line.groups() == 1 and _assign(line.x0, line.x0 + 1, spans) == 0
    )


def _row_cells(line: _Line, spans: list[tuple[float, float]]) -> list[list[_Word]]:
    row: list[list[_Word]] = [[] for _ in spans]
    if _is_label_line(line, spans):
        row[0] = list(line.words)
        return row
    for cell in _cells(line):
        cols = {_assign(w.x0, w.x1, spans) for w in cell}
        if not line.is_data() and len(cols) > 1:
            # Header cell spread over several columns ("EM F1 EM F1"): place word by word.
            for w in cell:
                row[_assign(w.x0, w.x1, spans)].append(w)
        else:
            row[_assign(cell[0].x0, cell[-1].x1, spans)].extend(cell)
    return row


def _cell_bold(words: list[_Word]) -> bool:
    """Bold if its numbers are bold ("±" is often set in a regular font), else all words."""
    numbers = [w for w in words if _is_num(w.text)]
    return bool(words) and all(w.bold for w in (numbers or words))


# ---- step 6: sanity


def grid_problem(table: TableData) -> str | None:
    """Why this grid should not be trusted, or None if it looks like a real table."""
    if table.n_rows < 2 or table.n_cols < 2:
        return "too small"
    filled = [c for c in table.cells if c.text.strip()]
    if not filled:
        return "empty"
    prose = sum(1 for c in filled if len(c.text.split()) >= 8)
    if prose / len(filled) > 0.15:
        return "looks like running text"
    return None


def reconstruct_table(
    page: pymupdf.Page, region: pymupdf.Rect, caption: str = "", label: str | None = None
) -> tuple[TableData, pymupdf.Rect] | None:
    """Rebuild a table grid from word positions.

    Returns the table and the region its rows occupy (header included, caption excluded), or
    None if no trustworthy grid is found.
    """
    region = pymupdf.Rect(region) & page.rect
    number = _caption_number(label)
    own_caption = _find_own_caption(page, number, region)
    col_x0, col_x1 = _column_bounds(page, region, own_caption)
    y0, y1 = region.y0 - 90, region.y1 + 90
    if own_caption is not None:
        y0, y1 = min(y0, own_caption.y0 - 5), max(y1, own_caption.y1 + 5)
    clip = pymupdf.Rect(col_x0, max(0.0, y0), col_x1, min(page.rect.height, y1))

    lines = _cluster_lines(_words(page, clip))
    if not lines:
        return None
    _classify(lines, number, col_x1 - col_x0)
    seg = _choose_segment(lines, _segments(lines), region)
    if seg is None:
        return None
    seg = _trim_leading_text(seg, _horizontal_rules(page, clip))

    spans = _column_spans(seg)
    if len(spans) < 2:
        return None
    rows: list[list[list[_Word]]] = []
    prev: _Line | None = None
    for line in seg:
        cells = _row_cells(line, spans)
        filled = sum(1 for c in cells if c)
        # Wrapped line: no numbers, fills under half the columns, tight under the previous line.
        # A section label starts its own row; only its own wrapped lines merge into it. A
        # lowercase start or a hyphen at the end of the line above means a wrapped cell
        # ("BERT-" / "base"), not a new label.
        continues = prev is not None and (
            line.text[:1].islower() or prev.words[0].text.endswith("-")
        )
        label_line = _is_label_line(line, spans) and not continues
        wrapped = (
            prev is not None
            and rows
            and not line.has_number()
            and filled < max(2, len(spans) / 2)
            and line.y0 - prev.y1 < 0.6 * (line.y1 - line.y0)
            and (not label_line or _is_label_line(prev, spans))
        )
        if wrapped:
            rows[-1] = [a + b for a, b in zip(rows[-1], cells, strict=True)]
        else:
            rows.append(cells)
        prev = line

    table = TableData(
        label=label,
        caption=caption,
        n_rows=len(rows),
        n_cols=len(spans),
        cells=[
            TableCell(
                text=_join_words(words),
                row=r,
                col=c,
                is_bold=_cell_bold(words),
            )
            for r, row in enumerate(rows)
            for c, words in enumerate(row)
        ],
    )
    normalize_table(table)
    if grid_problem(table) is not None:
        return None
    used = pymupdf.Rect(min(ln.x0 for ln in seg), seg[0].y0, max(ln.x1 for ln in seg), seg[-1].y1)
    return table, used


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
