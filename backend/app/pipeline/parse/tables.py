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

# A caption has punctuation right after the number: "Table 2:" / "Table 2." / "Table B.1.".
# "Table 2 shows ..." at the start of a body-text line is not a caption.
_TABLE_CAPTION_RE = re.compile(
    r"^\s*(?:Table|Tab\.|TABLE)\s*(?P<num>[A-Z]?\.?\d+(?:\.\d+)?)\s*[:.|]", re.IGNORECASE
)
_HEADING_RE = re.compile(r"^(?:\d+(?:\.\d+)*\.?|[A-Z](?:\.\d+)+\.?)\s+[A-Z][A-Za-z]")
_FIGURE_CAPTION_RE = re.compile(r"^\s*(?:Figure|Fig\.|FIGURE)\s*[A-Z]?\.?\d+", re.IGNORECASE)
MIN_COL_GAP = 4.0  # points; inter-word spaces are ~2-3 pt, LaTeX tabcolsep gives ~12 pt
NUM_COL_GAP = 1.0  # two numbers side by side are separate cells even when tightly packed
PROSE_GAP = 8.0  # justified prose stretches spaces, but not this far
_THOUSANDS_HEAD = re.compile(r"^\d{1,3}$")
_THOUSANDS_TAIL = re.compile(r"^\d{3}(?:[.,]\d+)?$")
_PROSE_WORD = re.compile(r"^[a-z][a-z\-']+[.,;:)]?$")
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

    @property
    def lowercase_words(self) -> int:
        """Plain lowercase dictionary-like words ("the", "results,"), not tokens like "c0"."""
        return sum(1 for w in self.words if _PROSE_WORD.match(w.text))

    def is_sentence_like(self) -> bool:
        """Running text: mostly lowercase words, whatever numbers it mentions."""
        n = len(self.words)
        return n >= 7 and self.lowercase_words >= 0.6 * n

    def has_number(self) -> bool:
        return any(parse_number(w.text) is not None for w in self.words)

    def is_data(self) -> bool:
        return self.n_numeric >= 2 or (self.n_numeric >= 1 and self.groups() >= 2)

    def is_text_row(self) -> bool:
        """A row of a table without numbers (e.g. complexity formulas): 3+ column groups."""
        return self.groups() >= 3


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
    prev: _Word | None = None
    for w in words:
        if prev is None:
            text = w.text
        elif prev.text.endswith("-") and (w.text[:1].islower() or w.x0 - prev.x1 < 1.5):
            text += w.text  # "multi-" / "crop", small caps "SEGMENT-" / "PAIR"
        elif w.text.startswith("-") and w.x0 - prev.x1 < 1.5:
            text += w.text  # "FULL" / "-SENTENCES"
        else:
            text += " " + w.text
        prev = w
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


def caption_label(text: str) -> str | None:
    """ "Table 3" from caption text like "Table 3: ..." or "TableB.5. ..."."""
    m = _TABLE_CAPTION_RE.match(text or "")
    return f"Table {m.group('num').lstrip('.')}" if m else None


def _caption_number(label: str | None) -> str | None:
    if not label:
        return None
    m = re.search(r"([A-Z]?\.?\d+(?:\.\d+)?)\s*$", label)
    return m.group(1).lstrip(".") if m else None


def _find_own_caption(
    page: pymupdf.Page, number: str | None, region: pymupdf.Rect, max_dist: float = 200.0
) -> pymupdf.Rect | None:
    """The caption line "Table <number>:" closest to the region (within max_dist pt)."""
    if number is None:
        return None
    best: tuple[float, pymupdf.Rect] | None = None
    for rect, text in _page_lines(page):
        m = _TABLE_CAPTION_RE.match(text)
        if not m or m.group("num").replace(".", "") != number.replace(".", ""):
            continue
        dist = max(0.0, region.y0 - rect.y1, rect.y0 - region.y1)
        if dist <= max_dist and (best is None or dist < best[0]):
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
    # Full-width table on a two-column page: a wide anchor, or one crossing the gutter (a
    # centred caption under a wide table can be short, but never fits in one column).
    if anchor.width > 0.55 * width or (anchor.x0 < mid - 15 and anchor.x1 > mid + 15):
        return 0.0, width
    centre = (anchor.x0 + anchor.x1) / 2
    return (0.0, mid + 4) if centre < mid else (mid - 4, width)


# ---- step 2: words and lines


def _running_heads(page: pymupdf.Page) -> list[pymupdf.Rect]:
    """Header lines (paper title, venue) repeated at the same height near the top of
    neighbouring pages. Short lines are ignored: table header cells like "Model" repeat too."""
    doc = page.parent
    band = 0.12 * page.rect.height

    def top_lines(p: pymupdf.Page) -> list[tuple[pymupdf.Rect, str]]:
        clip = pymupdf.Rect(0, 0, p.rect.width, band)
        return [(r, t) for r, t in _page_lines(p, clip) if len(t) >= 12]

    others: list[tuple[pymupdf.Rect, str]] = []
    for n in (page.number - 1, page.number + 1, page.number - 2, page.number + 2):
        if doc is not None and 0 <= n < doc.page_count:
            others += top_lines(doc[n])
    return [
        r for r, t in top_lines(page) if any(t == t2 and abs(r.y0 - r2.y0) < 2 for r2, t2 in others)
    ]


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
    top, bottom = 0.065 * page.rect.height, 0.94 * page.rect.height
    heads = _running_heads(page)
    for block in page.get_text("rawdict", clip=clip)["blocks"]:
        for line in block.get("lines", []):
            if line["bbox"][3] < top or line["bbox"][1] > bottom:
                continue  # page numbers, footers
            if any(pymupdf.Rect(line["bbox"]).intersects(h) for h in heads):
                continue  # running head
            dx, dy = line.get("dir", (1.0, 0.0))
            if abs(dy) > 0.1 or dx < 0:  # rotated text: margin stamps, axis labels
                continue
            for span in line["spans"]:
                font = span["font"].lower()
                bold = bool(span["flags"] & 16) or any(k in font for k in ("bold", "cmbx", "medi"))
                size = float(span["size"])
                current: list[dict[str, Any]] = []
                for ch in span["chars"]:
                    if current:
                        prev = current[-1]
                        gap = ch["bbox"][0] - prev["bbox"][2]
                        jump = abs(
                            (ch["bbox"][1] + ch["bbox"][3]) / 2
                            - (prev["bbox"][1] + prev["bbox"][3]) / 2
                        )
                        brk = (
                            gap > 0.3 * size  # word break without a space character
                            or gap < -0.5 * size  # text jumps back left: a new visual line
                            or jump > 0.6 * size  # stacked lines written in one span
                            or (prev["c"] in _DASHES and gap > 1.0)  # "-" cell, then a value
                        )
                    else:
                        brk = False
                    if ch["c"].isspace() or brk:
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
        if (
            prev is not None
            and w.x0 - prev.x1 < 2.2
            and _THOUSANDS_HEAD.match(prev.text)
            and _THOUSANDS_TAIL.match(w.text)
        ):
            # "20 000" with a thin space is one number, not two columns.
            merged[-1] = _Word(
                prev.x0,
                min(prev.y0, w.y0),
                w.x1,
                max(prev.y1, w.y1),
                prev.text + w.text,
                prev.bold or w.bold,
                prev.size,
            )
            continue
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
    # Measure against the widest line (the real text width), not the clip, which includes
    # page margins.
    col_width = min(col_width, max((ln.x1 - ln.x0 for ln in lines), default=col_width))
    left = min((ln.x0 for ln in lines), default=0.0)
    right = max((ln.x1 for ln in lines), default=0.0)
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
            _HEADING_RE.match(text)
            and len(line.words) <= 8
            and line.n_numeric <= 1
            and not any(c.isdigit() for c in text.split(" ", 1)[-1])
        ):
            line.kind = "heading"  # "4.3 Multi-crop evaluation": the table ended above
        elif (
            prev is not None
            and prev.kind.startswith("caption")
            and line.groups(PROSE_GAP) == 1
            and abs(line.size - prev.size) < 0.5
            and line.y0 - prev.y1 < 0.6 * (line.y1 - line.y0)
        ):
            line.kind = "caption_cont"  # wrapped caption text: same size, tightly spaced
        elif (
            # Justified body text spans margin to margin (allowing a paragraph indent); label
            # rows inside tables are centred or shorter.
            line.x0 - left < 14
            and right - line.x1 < 6
            and line.x1 - line.x0 >= 0.8 * col_width
            and len(line.words) >= 7
            and line.groups(PROSE_GAP) == 1
            and line.n_numeric <= 1
        ) or (
            line.x1 - line.x0 >= 0.5 * col_width
            and line.is_sentence_like()
            and line.lowercase_words >= 6
        ):
            line.kind = "prose"
        prev = line


@dataclass
class _Segment:
    lines: list[_Line]
    soft_before: bool  # separated from the previous segment only by vertical space
    gap_before: float


def _median_height(lines: list[_Line]) -> float:
    heights = sorted(ln.y1 - ln.y0 for ln in lines) or [10.0]
    return heights[len(heights) // 2]


def _segments(lines: list[_Line]) -> list[_Segment]:
    """Runs of row lines, split at captions/prose/headings (hard) and big gaps (soft)."""
    max_gap = 1.5 * _median_height(lines)
    segs: list[_Segment] = []
    current: list[_Line] = []
    soft, gap = False, 0.0
    for line in lines:
        if line.kind != "row":
            if current:
                segs.append(_Segment(current, soft, gap))
            current, soft, gap = [], False, 0.0
            continue
        if current and line.y0 - current[-1].y1 > max_gap:
            segs.append(_Segment(current, soft, gap))
            current, soft, gap = [], True, line.y0 - current[-1].y1
        current.append(line)
    if current:
        segs.append(_Segment(current, soft, gap))
    return segs


def _data_lines(seg: list[_Line]) -> int:
    """Numeric rows; for tables without numbers, rows with several column groups."""
    numeric = sum(1 for ln in seg if ln.is_data())
    return numeric or sum(1 for ln in seg if ln.is_text_row())


def _extent(segs: list[_Segment], k: int) -> tuple[int, int]:
    """Segment k plus neighbours separated from it only by a moderate gap: a header row or a
    block of rows set apart with extra space belongs to the same table."""
    limit = 3.5 * _median_height([ln for sg in segs for ln in sg.lines])
    lo = hi = k
    while lo > 0 and segs[lo].soft_before and segs[lo].gap_before <= limit:
        lo -= 1
    while hi + 1 < len(segs) and segs[hi + 1].soft_before and segs[hi + 1].gap_before <= limit:
        hi += 1
    return lo, hi


def _choose_segment(
    lines: list[_Line],
    segs: list[_Segment],
    region: pymupdf.Rect,
    caption_side: str | None = None,
) -> list[_Line] | None:
    """Pick the table's rows: the run next to its own caption, else the one overlapping the
    region the parser reported."""

    def joined(lo: int, hi: int) -> list[_Line]:
        return [ln for sg in segs[lo : hi + 1] for ln in sg.lines]

    def overlap(seg: list[_Line]) -> float:
        return max(0.0, min(seg[-1].y1, region.y1) - max(seg[0].y0, region.y0))

    seg_index = {id(ln): k for k, sg in enumerate(segs) for ln in sg.lines}
    own = [i for i, ln in enumerate(lines) if ln.kind == "caption_own"]
    if own:
        start = own[0]
        end = start
        while end + 1 < len(lines) and lines[end + 1].kind == "caption_cont":
            end += 1
        sides: dict[str, tuple[int, int]] = {}
        if start > 0 and (k := seg_index.get(id(lines[start - 1]))) is not None:
            sides["above"] = _extent(segs, k)
        if end + 1 < len(lines) and (k := seg_index.get(id(lines[end + 1]))) is not None:
            sides["below"] = _extent(segs, k)
        with_data_sides = {k for k, v in sides.items() if _data_lines(joined(*v)) > 0}
        if len(with_data_sides) == 2:
            # Which side is this caption's table on? Use the rules hugging the caption, else
            # the side with the smaller gap (caption-to-own-table spacing is the tightest).
            preferred = caption_side
            if preferred is None:
                gap_above = lines[start].y0 - segs[sides["above"][1]].lines[-1].y1
                gap_below = segs[sides["below"][0]].lines[0].y0 - lines[end].y1
                preferred = "above" if gap_above <= gap_below else "below"
            sides = {preferred: sides[preferred]}
        with_data = {k: v for k, v in sides.items() if _data_lines(joined(*v)) > 0}
        if with_data:
            lo, hi = max(with_data.values(), key=lambda v: _data_lines(joined(*v)))
            return joined(lo, hi)
    if not segs:
        return None
    k = max(
        range(len(segs)),
        key=lambda k: (
            overlap(segs[k].lines) > 0,
            _data_lines(segs[k].lines) > 0,
            overlap(segs[k].lines),
        ),
    )
    if overlap(segs[k].lines) <= 0 or _data_lines(segs[k].lines) == 0:
        return None
    return joined(*_extent(segs, k))


def _horizontal_rules(page: pymupdf.Page, clip: pymupdf.Rect) -> list[pymupdf.Rect]:
    rules: list[pymupdf.Rect] = []
    for drawing in page.get_drawings():
        r = pymupdf.Rect(drawing["rect"])
        # Rules are often zero-height lines; PyMuPDF treats those rects as empty, so
        # Rect.intersects() is always False for them. Compare coordinates directly.
        inside = clip.x0 <= r.x1 and r.x0 <= clip.x1 and clip.y0 <= r.y0 <= clip.y1
        if r.height <= 2.0 and r.width >= 20 and inside:
            rules.append(r)
    return rules


def _caption_side(rules: list[pymupdf.Rect], caption: pymupdf.Rect, col_width: float) -> str | None:
    """ "above" if the table's rule sits just above the caption (caption under the table),
    "below" if just below it, None if no rule is close."""
    near = [
        r for r in rules if r.width >= 0.25 * col_width and r.x1 > caption.x0 and r.x0 < caption.x1
    ]
    above = [caption.y0 - r.y1 for r in near if r.y1 <= caption.y0 + 1]
    below = [r.y0 - caption.y1 for r in near if r.y0 >= caption.y1 - 1]
    gap_above = min(above, default=None)
    gap_below = min(below, default=None)
    if gap_above is not None and gap_above < 20 and (gap_below is None or gap_above <= gap_below):
        return "above"
    if gap_below is not None and gap_below < 20:
        return "below"
    return None


def _is_fragment(line: _Line) -> bool:
    """A text line with no column structure that ends a sentence: the tail of a caption or
    paragraph next to the table ("ble 10 and 11 for better results.", "tions.")."""
    end = line.text.rstrip()[-1:]
    return line.groups() == 1 and (
        line.is_sentence_like()
        or (end in ".;" and (len(line.words) >= 2 or line.text[:1].islower()))
    )


def _trim_leading_text(seg: list[_Line], rules: list[pymupdf.Rect]) -> list[_Line]:
    """Drop body-text lines glued onto the top of the table (e.g. a paragraph's last line).

    A leading line goes if it has no column structure and either sits above the table's top
    rule (and has no numbers), or reads like the end of a sentence.
    """
    # A sentence fragment that mentions numbers ("...ResNets with 110 and 1202 layers.") is
    # not the first data row.
    first_data = next(
        (i for i, ln in enumerate(seg) if ln.is_data() and not _is_fragment(ln)), None
    )
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
        if (plain and above_rule) or _is_fragment(line):
            start += 1
        else:
            break
    return seg[start:]


def _trim_trailing_text(seg: list[_Line]) -> list[_Line]:
    """Drop sentence-like lines after the last data row (body text resuming below)."""
    last_data = max(
        (i for i, ln in enumerate(seg) if ln.is_data() and not _is_fragment(ln)), default=None
    )
    if last_data is None:
        return seg
    end = len(seg)
    while end - 1 > last_data:
        line = seg[end - 1]
        plain = not line.has_number() and line.groups() == 1
        if _is_fragment(line) or line.is_sentence_like() or (plain and len(line.words) >= 7):
            end -= 1
        else:
            break
    return seg[:end]


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
    return _split_by_reference_rows(spans, data)


def _split_by_reference_rows(
    spans: list[tuple[float, float]], data: list[_Line]
) -> list[tuple[float, float]]:
    """A span holding several cells of one data row is several columns (sparse columns,
    e.g. hyperparameter grids where most rows fill only one or two of them). Cut it at the
    gaps of the row with the most cells inside it."""
    out: list[tuple[float, float]] = []
    for a, b in spans:
        best: list[list[_Word]] = []
        for line in data:
            inside = [c for c in _cells(line) if c[0].x0 >= a - 0.5 and c[-1].x1 <= b + 0.5]
            if len(inside) > len(best):
                best = inside
        if len(best) < 2:
            out.append((a, b))
            continue
        cuts = [(p[-1].x1 + q[0].x0) / 2 for p, q in pairwise(best)]
        edges = [a, *cuts, b]
        out.extend(pairwise(edges))
    return out


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
        text = " ".join(w.text for w in cell)
        phrase = len(cell) >= 3 and (any(c.islower() for c in text) or "(" in text)
        if not line.is_data() and len(cols) > 1 and not phrase:
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


def locate_caption(
    pdf: pymupdf.Document, label: str | None, hint_page: int, hint: pymupdf.Rect | None = None
) -> tuple[int, pymupdf.Rect] | None:
    """Find "Table <n>:" in the document: the parser's page first, then its neighbours, then
    the rest. Parsers often report the wrong page or box for a table; its caption is reliable.
    Returns (1-based page, caption line rect)."""
    number = _caption_number(label)
    if number is None:
        return None
    order = [hint_page, hint_page + 1, hint_page - 1]
    order += [p for p in range(1, pdf.page_count + 1) if p not in order]
    for page_no in order:
        if not 1 <= page_no <= pdf.page_count:
            continue
        page = pdf[page_no - 1]
        region = hint if (hint is not None and page_no == hint_page) else page.rect
        rect = _find_own_caption(page, number, region, max_dist=page.rect.height)
        if rect is not None:
            return page_no, rect
    return None


def reconstruct_table(
    page: pymupdf.Page,
    region: pymupdf.Rect,
    caption: str = "",
    label: str | None = None,
    caption_rect: pymupdf.Rect | None = None,
) -> tuple[TableData, pymupdf.Rect] | None:
    """Rebuild a table grid from word positions.

    `region` is the parser's rough table box; `caption_rect` (from locate_caption) anchors the
    search when known. Returns the table and the region its rows occupy (header included,
    caption excluded), or None if no trustworthy grid is found.
    """
    region = pymupdf.Rect(region) & page.rect
    number = _caption_number(label)
    own_caption = caption_rect or _find_own_caption(page, number, region)
    col_x0, col_x1 = _column_bounds(page, region, own_caption)
    if own_caption is not None:
        # The table sits right above or below its caption.
        y0, y1 = own_caption.y0 - 420, own_caption.y1 + 420
    else:
        y0, y1 = region.y0 - 90, region.y1 + 90
    clip = pymupdf.Rect(col_x0, max(0.0, y0), col_x1, min(page.rect.height, y1))

    lines = _cluster_lines(_words(page, clip))
    if not lines:
        return None
    _classify(lines, number, col_x1 - col_x0)
    rules = _horizontal_rules(page, clip)
    side = _caption_side(rules, own_caption, col_x1 - col_x0) if own_caption else None
    seg = _choose_segment(lines, _segments(lines), region, side)
    if seg is None:
        return None
    seg = _trim_trailing_text(_trim_leading_text(seg, rules))
    if not seg:
        return None
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

    rows = _drop_noise_columns(rows)
    table = TableData(
        label=label,
        caption=caption,
        n_rows=len(rows),
        n_cols=len(rows[0]) if rows else 0,
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


def _drop_noise_columns(rows: list[list[list[_Word]]]) -> list[list[list[_Word]]]:
    """Remove columns made only of isolated letters: figure text drawn glyph by glyph next to
    the table (each letter its own 'word')."""
    if not rows:
        return rows
    keep = []
    for c in range(len(rows[0])):
        cells = [row[c] for row in rows if row[c]]
        letters = bool(cells) and all(
            all(len(w.text) <= 2 and w.text.isalpha() for w in cell) for cell in cells
        )
        # Sparse, header-less column of 1-2 character scraps (letters or lone digits).
        scraps = (
            bool(cells)
            and not rows[0][c]
            and len(cells) <= 0.4 * len(rows)
            and all(all(len(w.text) <= 2 for w in cell) for cell in cells)
        )
        noise = letters or scraps
        if not noise:
            keep.append(c)
    return [[row[c] for c in keep] for row in rows]


_NUMERIC_LIKE = re.compile(r"^[\d\s.,/±%()+\-–−*†‡∗^]+$")


def numeric_share(table: TableData) -> float:
    """Share of non-header cells that hold numbers ('57.5 / 62.8' and '90.4/78.7' count)."""
    body = [c for c in table.cells if not c.is_header and c.text.strip()]
    if not body:
        return 0.0
    numeric = sum(
        1
        for c in body
        if c.value is not None
        or (any(ch.isdigit() for ch in c.text) and _NUMERIC_LIKE.match(c.text))
    )
    return numeric / len(body)


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
