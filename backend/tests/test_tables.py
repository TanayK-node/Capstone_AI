from pathlib import Path

import pymupdf
import pytest

from app.pipeline.parse.tables import (
    grid_problem,
    normalize_table,
    parse_number,
    reconstruct_table,
    table_from_rows,
)

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize(
    ("text", "value", "std", "pct"),
    [
        ("24.3", 24.3, None, False),
        ("24.3 ± 0.2", 24.3, 0.2, False),
        ("24.3±0.2", 24.3, 0.2, False),
        ("84.6%", 84.6, None, True),
        ("84.6 (0.4)", 84.6, 0.4, False),
        ("−0.5", -0.5, None, False),  # noqa: RUF001 - unicode minus on purpose
        ("1,234", 1234.0, None, False),
        ("3e-4", 3e-4, None, False),
        ("88.0*", 88.0, None, False),
        ("71.2†", 71.2, None, False),
        (".85", 0.85, None, False),
    ],
)
def test_parse_number(text: str, value: float, std: float | None, pct: bool) -> None:
    num = parse_number(text)
    assert num is not None
    assert num.value == pytest.approx(value)
    assert num.std == (pytest.approx(std) if std is not None else None)
    assert num.is_percent is pct


@pytest.mark.parametrize("text", ["", "-", "BERT-base", "n/a", "ResNet-50", "Acc. (%)", "1.2.3"])
def test_parse_number_rejects_non_numbers(text: str) -> None:
    assert parse_number(text) is None


def test_normalize_detects_header_rows() -> None:
    table = normalize_table(
        table_from_rows([["", "BLEU", "chrF"], ["Model", "test", "test"], ["Ours", "26.4", "55"]])
    )
    assert table.header_rows == 2
    assert [c.is_header for c in table.cells if c.row == 2] == [False, False, False]


def _region(name: str, page: int) -> tuple[pymupdf.Page, pymupdf.Rect]:
    # GROBID's table boxes for the fixtures (they miss the header rows on purpose).
    boxes = {
        "paper_single": pymupdf.Rect(70.0, 238.5, 418.6, 320.8),
        "paper_twocol": pymupdf.Rect(334.2, 397.4, 533.3, 476.1),
    }
    doc = pymupdf.open(FIXTURES / f"{name}.pdf")
    return doc[page - 1], boxes[name]


def test_reconstructs_booktabs_table_with_std_and_bold() -> None:
    page, region = _region("paper_single", 2)
    result = reconstruct_table(page, region)
    assert result is not None
    table, _ = result
    assert table.grid() == [
        ["Method", "FLORES-200 BLEU", "WMT14 En-De BLEU", "FLOPs (%)"],
        ["Transformer", "24.3 ± 0.2", "27.1 ± 0.1", "100"],
        ["Switch", "25.0 ± 0.3", "27.4 ± 0.2", "72"],
        ["SparseRoute (ours)", "26.4 ± 0.2", "27.9 ± 0.1", "70"],
    ]
    assert table.header_rows == 1
    best = [(c.value, c.std) for c in table.cells if c.is_bold and not c.is_header]
    assert best == [(26.4, 0.2), (27.9, 0.1)]


def test_reconstructs_ruled_table_header_and_wrapped_cell() -> None:
    page, region = _region("paper_twocol", 1)
    result = reconstruct_table(page, region)
    assert result is not None
    table, used = result
    assert table.grid() == [
        ["Model", "Acc. (%)", "F1"],
        ["BERT-base", "84.6", "0.812"],  # "BERT-" / "base" wrapped onto two lines
        ["RoBERTa", "86.1", "0.829"],
        ["Ours", "88.0", "0.851"],
    ]
    assert used.y0 < region.y0  # region grew upward to include the header


def test_grid_problem_flags_running_text() -> None:
    prose = "this sentence is clearly running text from the body of the paper"
    bad = table_from_rows([["Model", "Score"], [prose, "1"], ["x", prose]])
    assert grid_problem(bad) == "looks like running text"
    good = table_from_rows([["Model", "Score"], ["Ours", "88.0"]])
    assert grid_problem(good) is None
    assert grid_problem(table_from_rows([["only one row"]])) == "too small"
