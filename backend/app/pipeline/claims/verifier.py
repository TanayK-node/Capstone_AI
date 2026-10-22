"""Claim verifier (M8): match a parsed claim to results-table cells and recompute it.

Verdicts (SCOPE.md F8), all decided here in Python:
  supported         the matching cells give the claimed value / delta / factor (± tolerance)
  contradicted      exactly one cell clearly is the claim's (method row, metric and dataset
                    column) and it disagrees: the paper's table says otherwise
  unsupported       tables with that metric exist but no cell gives the claimed number
  weakly_supported  a qualitative claim ("state of the art") with a table where the paper's
                    own method is best in at least one column
  unverifiable      nothing to check against (no table with that metric, no number)

"contradicted" needs a single unambiguous cell: a claim about a setting whose table was not
parsed must not be called false, so ambiguous misses stay "unsupported".
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from rapidfuzz import fuzz

from app.pipeline.extract.normalize import normalize_value
from app.schemas.claims import CheckedCell, ClaimCheck
from app.schemas.results import ResultCell, ResultColumn, ResultRow, ResultsTable

MATCH = 80.0  # name similarity (0-100) for "this column / row is the one the claim names"
STRONG = 90.0  # for a contradiction the match must be clear
FACTOR_TOLERANCE = 0.10  # factors ("10,000 times fewer") compare within 10 %

_LANG = {
    "english": "en", "german": "de", "french": "fr", "romanian": "ro", "chinese": "zh",
    "japanese": "ja", "czech": "cs", "russian": "ru", "spanish": "es", "finnish": "fi",
}  # fmt: skip
_GENERIC_BASELINE = re.compile(
    r"^$|previous|prior|existing|state[- ]of[- ]the[- ]art|sota|best|baselines?$|"
    r"all (other )?(methods|models)|competitors|other methods",
    re.I,
)
_OURS = re.compile(r"^$|\b(our|ours|we|proposed|this (paper|work))\b", re.I)
# A k / M / B suffix only when it stands alone: "2 BLEU" is 2, not 2 billion.
_FIRST_NUMBER = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?(?:\s*[kKmMbB](?![A-Za-z]))?")
_STOPWORDS = {"the", "of", "on", "and", "a", "an", "with", "for", "in", "by", "using"}
# Names papers write two ways ("MultiNLI" in the abstract, "MNLI" in the table header).
_ALIASES = {
    r"\bmulti ?nli\b": "mnli", r"\berr\b": "error", r"\bacc\b": "accuracy",
    r"\bppl\b": "perplexity", r"\bparams?\b": "parameters",
}  # fmt: skip
_SPLIT_WORDS = re.compile(r"\b(test|dev|val|validation|train|training)\b( set| split)?", re.I)


def norm(text: str) -> str:
    """Comparable name: lower case, language names as codes ("English-to-German" -> "en de"),
    citations and punctuation dropped."""
    t = re.sub(r"\[[\d,\s\u2013-]+\]", " ", text.lower())  # "[12]", "[3, 4]", "[5\u20137]"
    for name, code in _LANG.items():
        t = re.sub(rf"\b{name}\b", code, t)
    t = re.sub(r"\bto\b", " ", t)
    t = re.sub(r"\bfine[- ]?tun\w*", "ft", t)  # "fine-tuned with Adam" names the "(FT)" row
    t = re.sub(r"\bv(\d)", r"\1", t)  # "SQuAD v1.1" = "SQuAD 1.1"
    t = re.sub(r"[^a-z0-9]+", " ", t)
    for pattern, alias in _ALIASES.items():
        t = re.sub(pattern, alias, t)
    return t.strip()


def tokens(text: str) -> set[str]:
    return set(norm(text).split()) - _STOPWORDS


def name_score(wanted: str, text: str, ignore: set[str] | None = None) -> float:
    """0-100. 100 when every word `text` uses (minus `ignore`) appears in `wanted`: a header
    "BLEU EN-DE" fully names "WMT 2014 English-to-German" once the metric word is ignored,
    a row "GPT-3 (FT)" fully names "GPT-3 175B fine-tuned with Adam"."""
    a, b = norm(wanted), norm(text)
    if not a or not b:
        return 0.0
    words = tokens(text) - (ignore or set())
    if words and words <= tokens(wanted):
        return 100.0
    score = fuzz.token_set_ratio(a, b)
    if len(a) >= 3:
        score = max(score, fuzz.partial_ratio(a, b))
    return float(score)


def number(text: str) -> float | None:
    """First number in a claim fragment: '28.4' / 'over 2 BLEU' / '4.2%' / '10,000'."""
    m = _FIRST_NUMBER.search(text or "")
    return normalize_value(m.group(0)) if m else None


def close(a: float, b: float, tol: float) -> bool:
    """Equal within tolerance, also across percent / fraction (76.5 vs 0.765)."""
    return any(abs(a - x) <= tol for x in (b, b * 100, b / 100))


def satisfies(found: float, claimed: float, comparator: str, tol: float) -> bool:
    if comparator == "at_least":
        return found >= claimed - tol
    if comparator == "at_most":
        return found <= claimed + tol
    if comparator == "approx":
        return abs(found - claimed) <= max(tol, 0.05 * abs(claimed))
    return abs(found - claimed) <= tol


@dataclass
class _Col:
    table: ResultsTable
    column: ResultColumn
    metric: float
    dataset: float

    @property
    def name(self) -> str:
        return f"{self.column.group} {self.column.header}".strip()


def matching_columns(tables: list[ResultsTable], metric: str, dataset: str) -> list[_Col]:
    """Numeric columns whose header / group / caption name the claim's metric and dataset.
    An unnamed metric or dataset does not constrain."""
    out: list[_Col] = []
    for t in tables:
        for c in t.columns:
            if not c.numeric:
                continue
            m = _field_score(metric, c, t, ignore=tokens(dataset)) if metric else 100.0
            d = _field_score(dataset, c, t, ignore=tokens(metric)) if dataset else 100.0
            core = _SPLIT_WORDS.sub(" ", dataset).strip()  # "ImageNet test set" -> "ImageNet"
            if core and core != dataset:
                d = max(d, 0.95 * _field_score(core, c, t, ignore=tokens(metric)))
            if m >= MATCH and d >= MATCH:
                out.append(_Col(t, c, m, d))
    # Clearest match first, so a column named only by its caption never wins over one
    # whose own header names the metric and dataset.
    out.sort(key=lambda c: (min(c.metric, c.dataset), c.metric + c.dataset), reverse=True)
    return out


def _field_score(wanted: str, column: ResultColumn, table: ResultsTable, ignore: set[str]) -> float:
    # The caption is long: only fuzzy (never "every word named") and weighted down.
    caption = fuzz.partial_ratio(norm(wanted), norm(table.caption)) if len(norm(wanted)) >= 3 else 0
    return max(
        name_score(wanted, column.header, ignore),
        0.95 * name_score(wanted, column.group, ignore),
        0.85 * caption,
    )


def method_rows(table: ResultsTable, method: str) -> list[tuple[ResultRow, float]]:
    """Rows of the claim's method: the paper's own rows when it says "our model", else rows
    named like it."""
    rows: list[tuple[ResultRow, float]] = []
    for row in table.rows:
        if _OURS.search(method.strip()) and row.is_proposed:
            rows.append((row, 100.0))
        elif method and (s := name_score(method, row.label)) >= MATCH:
            rows.append((row, s))
    return rows


def baseline_rows(
    table: ResultsTable, baseline: str, col: ResultColumn
) -> list[tuple[ResultRow, float]]:
    """Rows named like the baseline; for "the previous best" / "state of the art", the best
    row that is not the paper's own method in this column."""
    if baseline and not _GENERIC_BASELINE.search(baseline.strip()):
        return [
            (r, s)
            for r in table.rows
            if not r.is_proposed and (s := name_score(baseline, r.label)) >= MATCH - 5
        ]
    others = [(r, _cell(r, col.index)) for r in table.rows if not r.is_proposed]
    scored = [(r, c.value) for r, c in others if c is not None and c.value is not None]
    if not scored:
        return []
    lower = col.higher_is_better is False
    best = min(scored, key=lambda x: x[1]) if lower else max(scored, key=lambda x: x[1])
    return [(best[0], 75.0)]  # a guess at what "previous best" means: never "strong"


def _cell(row: ResultRow, col: int) -> ResultCell | None:
    return next((c for c in row.cells if c.col == col), None)


def _checked(col: _Col, row: ResultRow, cell: ResultCell, role: str) -> CheckedCell:
    assert cell.value is not None
    return CheckedCell(
        table_id=col.table.table_id,
        table_label=col.table.label,
        row=row.index,
        col=cell.col,
        row_label=row.label,
        column=col.name,
        text=cell.text,
        value=cell.value,
        role=role,
    )


# ------------------------------------------------------------------ verdicts


def verify(claim: ClaimCheck, tables: list[ResultsTable], tol: float) -> None:
    if claim.kind == "qualitative":
        _qualitative(claim, tables)
        return
    cols = matching_columns(tables, claim.metric, claim.dataset)
    if not cols:
        claim.verdict = "unverifiable"
        what = " / ".join(x for x in (claim.metric, claim.dataset) if x) or "this claim"
        claim.explanation = f"No results table has a column for {what}."
        return
    if claim.kind == "score":
        _score(claim, cols, tol)
    else:
        _comparison(claim, cols, tol)


def _score(claim: ClaimCheck, cols: list[_Col], tol: float) -> None:
    if claim.claimed_value is None:
        claim.verdict, claim.explanation = "unverifiable", "No value to check."
        return
    strong: list[tuple[_Col, ResultRow, ResultCell]] = []
    for col in cols:
        for row, row_score in method_rows(col.table, claim.method):
            cell = _cell(row, col.column.index)
            if cell is None or cell.value is None:
                continue
            if close(claim.claimed_value, cell.value, tol):
                claim.verdict = "supported"
                claim.table_value = cell.value
                claim.checked_cells = [_checked(col, row, cell, "method")]
                claim.explanation = (
                    f"{col.table.label or 'Table'}: {row.label}, {col.name} = {cell.text}."
                )
                return
            if row_score >= STRONG and min(col.metric, col.dataset) >= STRONG:
                strong.append((col, row, cell))
    if len(strong) == 1:
        col, row, cell = strong[0]
        claim.verdict = "contradicted"
        claim.table_value = cell.value
        claim.checked_cells = [_checked(col, row, cell, "method")]
        claim.explanation = (
            f"The paper claims {claim.claimed_value:g}, but {col.table.label or 'the table'} "
            f"gives {row.label}, {col.name} = {cell.text}."
        )
        return
    claim.verdict = "unsupported"
    claim.checked_cells = [_checked(c, r, x, "method") for c, r, x in strong[:4]]
    claim.explanation = (
        f"No cell of the paper's method gives {claim.claimed_value:g} in a matching column."
    )


def _comparison(claim: ClaimCheck, cols: list[_Col], tol: float) -> None:
    """improvement (method minus baseline) and factor (ratio) claims."""
    if claim.claimed_delta is None:
        claim.verdict, claim.explanation = "unverifiable", "No amount to check."
        return
    tried: list[tuple[_Col, ResultRow, ResultCell, ResultRow, ResultCell, float, float]] = []
    for col in cols:
        for m_row, m_score in method_rows(col.table, claim.method):
            m_cell = _cell(m_row, col.column.index)
            if m_cell is None or m_cell.value is None:
                continue
            for b_row, b_score in baseline_rows(col.table, claim.baseline, col.column):
                b_cell = _cell(b_row, col.column.index)
                if b_cell is None or b_cell.value is None or b_row is m_row:
                    continue
                ok = _recompute(claim, col.column, m_cell.value, b_cell.value, tol)
                if ok:
                    claim.verdict = "supported"
                    claim.checked_cells = [
                        _checked(col, m_row, m_cell, "method"),
                        _checked(col, b_row, b_cell, "baseline"),
                    ]
                    claim.explanation = _explain(claim, col, m_row, m_cell, b_row, b_cell)
                    return
                tried.append((col, m_row, m_cell, b_row, b_cell, min(m_score, b_score), col.metric))
    strong = [t for t in tried if t[5] >= STRONG and min(t[0].metric, t[0].dataset) >= STRONG]
    if len(strong) == 1:
        col, m_row, m_cell, b_row, b_cell, _, _ = strong[0]
        assert m_cell.value is not None and b_cell.value is not None
        _recompute(claim, col.column, m_cell.value, b_cell.value, tol)  # fill the numbers
        claim.verdict = "contradicted"
        claim.checked_cells = [
            _checked(col, m_row, m_cell, "method"),
            _checked(col, b_row, b_cell, "baseline"),
        ]
        claim.explanation = "Recomputed from the table: " + _explain(
            claim, col, m_row, m_cell, b_row, b_cell
        )
        return
    claim.verdict = "unsupported"
    if tried:
        # Report the clearest pair: best row match, then best column match.
        tried.sort(key=lambda t: (t[5], min(t[0].metric, t[0].dataset)), reverse=True)
        col, m_row, m_cell, b_row, b_cell, _, _ = tried[0]
        assert m_cell.value is not None and b_cell.value is not None
        _recompute(claim, col.column, m_cell.value, b_cell.value, tol)
        claim.checked_cells = [
            _checked(col, m_row, m_cell, "method"),
            _checked(col, b_row, b_cell, "baseline"),
        ]
        claim.explanation = "Closest pair found does not give the claimed amount: " + _explain(
            claim, col, m_row, m_cell, b_row, b_cell
        )
    else:
        claim.explanation = "No method / baseline pair found in a matching column."


def _recompute(
    claim: ClaimCheck, column: ResultColumn, method: float, baseline: float, tol: float
) -> bool:
    """Fill the recomputed numbers and say whether they give the claimed amount."""
    assert claim.claimed_delta is not None
    lower = column.higher_is_better is False or claim.direction == "lower"
    claim.table_value, claim.baseline_value = method, baseline
    gain = (baseline - method) if lower else (method - baseline)  # improvement, sign-aware
    claim.recomputed_delta = round(method - baseline, 4)
    claim.recomputed_relative = round(100 * gain / abs(baseline), 3) if baseline else None
    if claim.kind == "factor":
        factor = (
            (baseline / method if lower else method / baseline) if method and baseline else None
        )
        claim.recomputed_factor = round(factor, 3) if factor else None
        if factor is None:
            return False
        d = claim.claimed_delta
        if claim.comparator == "at_least":
            return factor >= d * (1 - FACTOR_TOLERANCE)
        if claim.comparator == "at_most":
            return factor <= d * (1 + FACTOR_TOLERANCE)
        return abs(factor - d) <= FACTOR_TOLERANCE * d
    if gain < 0:
        return False  # the method is worse than the baseline in this column
    candidates = [gain]
    if claim.delta_unit == "percent" and claim.recomputed_relative is not None:
        candidates.append(claim.recomputed_relative)  # "4.2%" may be points or relative
    return any(satisfies(x, claim.claimed_delta, claim.comparator, tol) for x in candidates)


def _explain(
    claim: ClaimCheck,
    col: _Col,
    m_row: ResultRow,
    m_cell: ResultCell,
    b_row: ResultRow,
    b_cell: ResultCell,
) -> str:
    where = f"{col.table.label or 'Table'}, {col.name}"
    if claim.kind == "factor":
        return (
            f"{where}: {m_row.label} {m_cell.text} vs {b_row.label} {b_cell.text} "
            f"= {claim.recomputed_factor:g}x (claimed {claim.claimed_delta:g}x)."
        )
    rel = f", {claim.recomputed_relative:+.2f}% relative" if claim.recomputed_relative else ""
    return (
        f"{where}: {m_row.label} {m_cell.text} vs {b_row.label} {b_cell.text} "
        f"= {claim.recomputed_delta:+g}{rel} (claimed {claim.claimed_delta:g}"
        f"{'%' if claim.delta_unit == 'percent' else ''})."
    )


def _qualitative(claim: ClaimCheck, tables: list[ResultsTable]) -> None:
    for t in tables:
        for row in t.rows:
            if not row.is_proposed:
                continue
            best = [c for c in row.cells if c.is_best and c.value is not None]
            if best:
                col = next(c for c in t.columns if c.index == best[0].col)
                claim.verdict = "weakly_supported"
                claim.checked_cells = [_checked(_Col(t, col, 100, 100), row, best[0], "method")]
                claim.explanation = (
                    f"{t.label or 'A table'}: the paper's {row.label} is best in "
                    f"{len(best)} column(s); the claim itself has no number to check."
                )
                return
    claim.verdict = "unverifiable"
    claim.explanation = "No number to check, and no table where the paper's method is best."
