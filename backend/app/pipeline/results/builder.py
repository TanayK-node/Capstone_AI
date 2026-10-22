"""Results tables (M9): typed rows / columns, best values, flat ResultEntry list.

Deterministic, from the parsed table grids (tables.reconstruct_table already typed every
cell: value, std, percent, bold). What this adds:
  * column headers from the header rows; a spanning label in an upper header row is kept as
    the column's `group` only where the column has no label of its own at that level,
  * row labels (leading text cells), group rows ("Methods using ResNet-50:"),
  * the proposed method's rows (row label mentions "ours" or the paper's method name),
  * best value per numeric column, with the direction guessed from the header
    (error / loss / perplexity / latency / params: lower is better).
"""

from __future__ import annotations

import re

from rapidfuzz import fuzz

from app.pipeline.extract.normalize import normalize_value
from app.pipeline.parse.tables import numeric_share
from app.schemas.document import Block, ParsedDocument
from app.schemas.extraction import PaperExtraction, ResultEntry
from app.schemas.results import ResultCell, ResultColumn, ResultRow, ResultsTable

MIN_NUMERIC_SHARE = 0.3  # below this the "table" is text (hyperparameter lists, examples)

_LOWER_BETTER = re.compile(
    r"\b(err(or)?s?|loss|perplexity|ppl|wer|cer|ter|latency|time|hours?|days|seconds|ms|"
    r"params?|parameters|flops|cost|memory|size|mse|mae|rmse|fid|bpc|bpd|nll)\b|#",
    re.I,
)
_HIGHER_BETTER = re.compile(
    r"\b(acc(uracy)?|top-?[15]|f1|bleu|rouge|meteor|met|cider|nist|map|ap\d*|auc|em|"
    r"exact match|precision|recall|score|mcc|pearson|spearman|ndcg|mrr|hits@\d+|psnr|ssim|"
    r"iou|miou|glue|avg|average|win rate)\b",
    re.I,
)
_OURS = re.compile(r"\(?\bours\b\)?|\bproposed\b", re.I)
# Title words that are never a method name ("Deep Residual Learning", "VERY DEEP ...").
_STOP = {
    "the", "and", "for", "with", "from", "via", "using", "towards", "learning", "deep",
    "neural", "networks", "network", "large", "scale", "image", "language", "models",
    "model", "pre", "training", "simple", "framework", "very", "all", "you", "need",
}  # fmt: skip


def build_results(doc: ParsedDocument, extraction: PaperExtraction | None) -> list[ResultsTable]:
    names = proposed_names(doc, extraction)
    tables: list[ResultsTable] = []
    for block in doc.tables:
        table = build_table(block, names)
        if table is not None:
            tables.append(table)
    return tables


def result_entries(
    tables: list[ResultsTable], extraction: PaperExtraction | None
) -> list[ResultEntry]:
    """Flat (method, dataset, metric, value) rows, the shape SCOPE.md §6 stores."""
    datasets = [d.name or d.value for d in extraction.datasets] if extraction else []
    metrics = [m.value for m in extraction.metrics] if extraction else []
    out: list[ResultEntry] = []
    for t in tables:
        for col in t.columns:
            if not col.numeric:
                continue
            context = f"{col.group} {col.header}"
            metric = _best_name(context, metrics) or _best_name(t.caption, metrics) or col.header
            dataset = _best_name(context, datasets) or _best_name(t.caption, datasets) or ""
            for row in t.rows:
                cell = next((c for c in row.cells if c.col == col.index), None)
                if cell is None or cell.value is None or not row.label:
                    continue
                out.append(
                    ResultEntry(
                        method=row.label,
                        dataset=dataset,
                        metric=metric,
                        value=cell.value,
                        std=cell.std,
                        is_proposed=row.is_proposed,
                        is_best=cell.is_best,
                        table_id=t.table_id,
                        cell=(row.index, col.index),
                    )
                )
    return out


# ------------------------------------------------------------------ one table


_PAIR = re.compile(r"^\s*([-+]?\d+(?:\.\d+)?)\s*/\s*[-+]?\d+(?:\.\d+)?\s*$")


def cell_value(text: str, parsed: float | None) -> float | None:
    """The parser's number, else a suffixed count ("354.92M" -> 354920000) or the first of
    a pair ("86.7/85.9", MNLI matched / mismatched: the text is kept as written)."""
    if parsed is not None:
        return parsed
    if m := _PAIR.match(text):
        return float(m.group(1))
    return normalize_value(text) if re.search(r"\d\s*[kKmMbB]\s*$", text) else None


def build_table(block: Block, names: list[str]) -> ResultsTable | None:
    data = block.table
    if data is None or data.n_rows < 2 or data.n_cols < 2:
        return None
    if numeric_share(data) < MIN_NUMERIC_SHARE:
        return None
    grid = data.grid()
    cells = {(c.row, c.col): c for c in data.cells}
    header_rows = max(1, data.header_rows) if data.header_rows < data.n_rows else 1
    label_cols = _label_columns(data.n_rows, data.n_cols, header_rows, cells)
    # A last "header" row with text only under the row labels is a section row that follows
    # the header ("Methods using ResNet-50:"), not part of it.
    while header_rows > 1 and all(
        not grid[header_rows - 1][c].strip() for c in range(data.n_cols) if c not in label_cols
    ):
        header_rows -= 1

    spans = _spanning_labels(grid, header_rows, data.n_cols, label_cols)
    columns: list[ResultColumn] = []
    for col in range(data.n_cols):
        own = [grid[r][col].strip() for r in range(header_rows) if grid[r][col].strip()]
        group = "" if own and header_rows == 1 else spans.get(col, "")
        body = [cells.get((r, col)) for r in range(header_rows, data.n_rows)]
        numeric = col not in label_cols and any(
            c is not None and cell_value(c.text, c.value) is not None for c in body
        )
        header = " ".join(own)
        columns.append(
            ResultColumn(
                index=col,
                header=header,
                group=group if group and group not in header else "",
                numeric=numeric,
                higher_is_better=_column_direction(header, group, block.text) if numeric else None,
            )
        )

    rows: list[ResultRow] = []
    group_label = ""
    for r in range(header_rows, data.n_rows):
        label = " ".join(grid[r][c].strip() for c in label_cols if grid[r][c].strip())
        values = [cells.get((r, c)) for c in range(data.n_cols) if c not in label_cols]
        if label and all(v is None or not v.text.strip() for v in values):
            group_label = label.rstrip(":")  # a section row: "Methods using ResNet-50:"
            continue
        row = ResultRow(
            index=r,
            label=label,
            group=group_label,
            is_proposed=bool(label) and _is_proposed(label, names),
        )
        for c in range(data.n_cols):
            cell = cells.get((r, c))
            if c in label_cols or cell is None or not cell.text.strip():
                continue
            row.cells.append(
                ResultCell(
                    col=c,
                    text=cell.text,
                    value=cell_value(cell.text, cell.value),
                    std=cell.std,
                    is_percent=cell.is_percent,
                    is_bold=cell.is_bold,
                )
            )
        rows.append(row)

    table = ResultsTable(
        table_id=block.id,
        label=block.label or data.label,
        caption=block.text,
        page=block.page,
        columns=columns,
        rows=rows,
        proposed_names=names,
    )
    _mark_best(table)
    return table


def _label_columns(n_rows: int, n_cols: int, header_rows: int, cells: dict) -> set[int]:  # type: ignore[type-arg]
    """Leading columns whose body cells are mostly text: the row labels."""
    out: set[int] = set()
    for col in range(n_cols - 1):  # the last column is never only a label
        body = [cells.get((r, col)) for r in range(header_rows, n_rows)]
        filled = [c for c in body if c is not None and c.text.strip()]
        if not filled:
            if col == 0:
                out.add(col)
                continue
            break
        texty = sum(1 for c in filled if cell_value(c.text, c.value) is None) / len(filled)
        if texty >= 0.6:
            out.add(col)
        else:
            break
    return out or {0}


def _spanning_labels(
    grid: list[list[str]], header_rows: int, n_cols: int, label_cols: set[int]
) -> dict[int, str]:
    """Guess which upper-row label spans each data column. A centred spanning header can sit
    in any of its columns, so the result is stored as `group`, never as the column's header.

    If the leaf header row repeats with a period p ("EN-DE EN-FR EN-DE EN-FR"), the data
    columns form blocks of p and each block takes the label found inside it (Transformer:
    BLEU over 1-2, Training Cost over 3-4). Otherwise each column takes the nearest label to
    its left (forward fill), never crossing into the row-label columns."""
    data_cols = [c for c in range(n_cols) if c not in label_cols]
    leaf = [grid[header_rows - 1][c].strip() for c in data_cols]
    period = _period(leaf)
    out: dict[int, list[str]] = {c: [] for c in data_cols}
    for r in range(header_rows - 1):
        if period:
            for start in range(0, len(data_cols), period):
                block = data_cols[start : start + period]
                found = [grid[r][c].strip() for c in block if grid[r][c].strip()]
                for c in block:
                    if found:
                        out[c].append(found[0])
            continue
        current = ""
        for c in data_cols:
            text = grid[r][c].strip()
            if text:
                # Text right below it means a header wrapped over two lines ("# Trainable /
                # Parameters"), not a label spanning the next columns.
                below = grid[header_rows - 1][c].strip() if r < header_rows - 1 else ""
                current = "" if below else text
                out[c].append(text)
            elif current:
                out[c].append(current)
    return {c: " ".join(v) for c, v in out.items() if v}


def _period(leaf: list[str]) -> int | None:
    """Smallest p > 1 such that the labels repeat every p columns, e.g. [a, b, a, b] -> 2."""
    if len(leaf) < 4 or not all(leaf):
        return None
    for p in range(2, len(leaf) // 2 + 1):
        if len(leaf) % p == 0 and all(leaf[i] == leaf[i + p] for i in range(len(leaf) - p)):
            return p
    return None


def _direction(header: str) -> bool | None:
    if _LOWER_BETTER.search(header):
        return False
    if _HIGHER_BETTER.search(header):
        return True
    return None


def _column_direction(header: str, group: str, caption: str) -> bool | None:
    """The column's own header decides; then its (guessed) group label; then the caption."""
    for text in (header, group):
        if (d := _direction(text)) is not None:
            return d
    return _caption_direction(caption)


def _caption_direction(caption: str) -> bool | None:
    """Fallback for headers like "QQP": the caption says what is measured. Only trusted when
    it names higher-is-better measures and no lower-is-better ones."""
    if _HIGHER_BETTER.search(caption) and not _LOWER_BETTER.search(caption):
        return True
    return None


def _mark_best(table: ResultsTable) -> None:
    for col in table.columns:
        if not col.numeric or col.higher_is_better is None:
            continue
        cells = [c for row in table.rows for c in row.cells if c.col == col.index]
        values = [c.value for c in cells if c.value is not None]
        if len(values) < 2:
            continue
        best = max(values) if col.higher_is_better else min(values)
        for c in cells:
            c.is_best = c.value == best


# ------------------------------------------------------------------ proposed method


def proposed_names(doc: ParsedDocument, extraction: PaperExtraction | None) -> list[str]:
    """Names the paper's own method goes by: the title's acronym or "Name:" prefix, plus
    capitalised names the method summary keeps repeating ("the Transformer")."""
    title = (extraction.metadata.title if extraction else None) or doc.metadata.title or ""
    names: list[str] = []
    head = title.split(":")[0].strip() if ":" in title else ""
    if head and len(head.split()) <= 3:
        names.append(head)  # "BERT: Pre-training ...", "LoRA: Low-Rank ..."
    words = re.findall(r"\b[A-Za-z][A-Za-z0-9-]{2,}\b", title)
    shouting = sum(w.isupper() for w in words) > 0.6 * max(1, len(words))  # ALL-CAPS title
    for word in words:
        mixed = any(ch.isupper() for ch in word[1:]) and not word.isupper()  # RoBERTa, LoRA
        acronym = word.isupper() and len(word) <= 8 and not shouting
        if (mixed or acronym) and word.lower() not in _STOP:
            names.append(word)
    if extraction:
        text = " ".join(i.value for i in extraction.method_summary + extraction.contributions)
        counts: dict[str, int] = {}
        for word in re.findall(r"\b[A-Z][A-Za-z0-9-]{2,}\b", text):
            if word.lower() not in _STOP:
                counts[word] = counts.get(word, 0) + 1
        names += [w for w, n in counts.items() if n >= 2]
    out: list[str] = []
    for n in names:
        if n.lower() not in {o.lower() for o in out}:
            out.append(n)
    return out[:6]


def _is_proposed(label: str, names: list[str]) -> bool:
    if _OURS.search(label):
        return True
    squashed = label.replace(" ", "").lower()
    return any(re.search(rf"\b{re.escape(n)}", label, re.I) or n.lower() in squashed for n in names)


def _best_name(text: str, names: list[str]) -> str | None:
    """The extracted dataset / metric name that best appears in a header or caption."""
    best, score = None, 0.0
    low = text.lower()
    for name in names:
        n = name.strip()
        if not n:
            continue
        s = 100.0 if n.lower() in low else fuzz.partial_ratio(n.lower(), low)
        if s > score:
            best, score = n, s
    return best if score >= 90 else None
