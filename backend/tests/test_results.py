"""Results tables (M9): headers, spans, row labels, values, proposed rows, best values."""

from app.pipeline.parse.tables import normalize_table, parse_number
from app.pipeline.results.builder import build_table, cell_value, proposed_names, result_entries
from app.schemas.document import Block, PageInfo, ParsedDocument, TableCell, TableData
from app.schemas.extraction import Item, PaperExtraction


def table_block(grid: list[list[str]], caption: str = "Table 1: Results.", bold=()) -> Block:  # type: ignore[no-untyped-def]
    cells = []
    for r, row in enumerate(grid):
        for c, text in enumerate(row):
            num = parse_number(text)
            cells.append(
                TableCell(text=text, row=r, col=c, value=num.value if num else None,
                          std=num.std if num else None, is_bold=(r, c) in bold)
            )  # fmt: skip
    data = normalize_table(TableData(label="Table 1", caption=caption, n_rows=len(grid),
                                     n_cols=len(grid[0]), cells=cells))  # fmt: skip
    return Block(id="b9", type="table", order=0, page=3, bbox=None, text=caption,
                 table=data, label="Table 1")  # fmt: skip


def test_columns_rows_best_and_proposed() -> None:
    block = table_block(
        [
            ["Method", "Top-1 Acc.", "Error (%)", "Params"],
            ["Methods using ResNet-50:", "", "", ""],
            ["MoCo", "60.6", "39.4", "24M"],
            ["SimCLR (ours)", "69.3", "30.7", "24M"],
        ]
    )
    t = build_table(block, names=[])
    assert t is not None
    cols = {c.header: c for c in t.columns}
    assert cols["Top-1 Acc."].higher_is_better is True
    assert cols["Error (%)"].higher_is_better is False  # lower is better
    assert [r.label for r in t.rows] == ["MoCo", "SimCLR (ours)"]
    assert t.rows[0].group == "Methods using ResNet-50"  # section row became a group
    ours = t.rows[1]
    assert ours.is_proposed
    best = {c.col: c.is_best for c in ours.cells}
    assert best[1] and best[2]  # highest accuracy, lowest error
    assert next(c for c in ours.cells if c.col == 3).value == 24e6  # "24M" read as a number


def test_periodic_leaf_headers_split_spanning_groups() -> None:
    """Transformer Table 2: BLEU spans EN-DE/EN-FR, Training Cost spans the next two."""
    block = table_block(
        [
            ["", "BLEU", "", "", "Training Cost (FLOPs)"],
            ["Model", "EN-DE", "EN-FR", "EN-DE", "EN-FR"],
            ["ConvS2S", "25.16", "40.46", "9.6e18", "1.5e20"],
            ["Transformer (big)", "28.4", "41.8", "2.3e19", "2.3e19"],
        ]
    )
    t = build_table(block, names=["Transformer"])
    assert t is not None
    groups = [c.group or c.header for c in t.columns[1:]]
    assert groups[1] == "BLEU" and groups[2].startswith("Training Cost")
    assert [c.higher_is_better for c in t.columns[1:]] == [True, True, False, False]
    assert t.rows[1].is_proposed


def test_wrapped_header_does_not_span_and_pairs_parse() -> None:
    block = table_block(
        [
            ["Model", "# Trainable", "", "MNLI"],
            ["", "Parameters", "BLEU", "m/mm"],
            ["GPT-2 (LoRA)", "0.35M", "70.4", "86.7/85.9"],
            ["GPT-2 (FT)", "354.92M", "68.2", "84.6/83.4"],
        ]
    )
    t = build_table(block, names=["LoRA"])
    assert t is not None
    bleu = next(c for c in t.columns if c.header == "BLEU")
    assert bleu.group == "" and bleu.higher_is_better is True  # not "# Trainable"
    assert [r.label for r in t.rows] == ["GPT-2 (LoRA)", "GPT-2 (FT)"]  # params not in label
    mnli = next(c for c in t.rows[0].cells if c.col == 3)
    assert mnli.value == 86.7 and mnli.text == "86.7/85.9"
    assert cell_value("1.2k", None) == 1200.0 and cell_value("n/a", None) is None


def test_text_tables_are_not_results() -> None:
    block = table_block([["Name", "Value"], ["optimizer", "Adam"], ["schedule", "cosine"]])
    assert build_table(block, names=[]) is None


def test_proposed_names_and_entries() -> None:
    page = PageInfo(number=1, width=1, height=1)
    doc = ParsedDocument(parser="t", parser_version="0", pages=[page], blocks=[])
    ex = PaperExtraction()
    ex.metadata.title = "RoBERTa: A Robustly Optimized BERT Pretraining Approach"
    ex.method_summary = [
        Item(id="m", value="RoBERTa trains longer"),
        Item(id="n", value="RoBERTa drops NSP"),
    ]
    assert proposed_names(doc, ex)[:2] == ["RoBERTa", "BERT"]
    ex.metrics = [Item(id="x", value="accuracy")]
    block = table_block([["Model", "SST-2 accuracy"], ["BERT", "93.5"], ["RoBERTa", "96.4"]])
    t = build_table(block, names=["RoBERTa"])
    assert t is not None
    entries = result_entries([t], ex)
    assert [(e.method, e.metric, e.value, e.is_best) for e in entries] == [
        ("BERT", "accuracy", 93.5, False),
        ("RoBERTa", "accuracy", 96.4, True),
    ]
