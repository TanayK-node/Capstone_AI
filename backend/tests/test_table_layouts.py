"""Table reconstruction on layouts that broke on real arXiv papers (Phase 1 report).

Each test renders a small PDF that reproduces one failure mode, passes a deliberately sloppy
region (as GROBID does), and checks the grid. Rendering is fast, so nothing is committed.
"""

from pathlib import Path

import pymupdf
import pytest

from app.pipeline.parse.tables import reconstruct_table
from tests.fixtures.make_fixtures import FILLER, render

TIGHT_CSS = "td, th { padding: 1pt 1.2pt; }"


def pdf(tmp_path: Path, html: str, columns: int = 1, name: str = "t.pdf") -> pymupdf.Document:
    out = tmp_path / name
    render(html, out, columns=columns)
    return pymupdf.open(out)


def rect_of(page: pymupdf.Page, text: str) -> pymupdf.Rect:
    hits = page.search_for(text)
    assert hits, f"{text!r} not on page"
    return pymupdf.Rect(hits[0])


def grid(page: pymupdf.Page, region: pymupdf.Rect, label: str | None) -> list[list[str]]:
    result = reconstruct_table(page, region, label=label)
    assert result is not None, "no grid"
    return result[0].grid()


TABLE_A = """
<table>
<tr><th>Model</th><th>Acc.</th><th>F1</th></tr>
<tr><td>BERT-base</td><td>84.6</td><td>0.812</td></tr>
<tr><td>RoBERTa</td><td>86.1</td><td>0.829</td></tr>
<tr><td>Ours</td><td><b>88.0</b></td><td><b>0.851</b></td></tr>
</table>
"""


def test_two_column_page_ignores_the_other_columns_prose(tmp_path: Path) -> None:
    html = (
        f"<p>{FILLER * 9}</p>{TABLE_A}<p class='caption'>Table 2: Accuracy.</p><p>{FILLER * 6}</p>"
    )
    page = pdf(tmp_path, html, columns=2)[0]
    model = rect_of(page, "RoBERTa")
    assert model.x0 > page.rect.width / 2, "fixture: table should be in the right column"
    # GROBID-style box that spans both columns around the table.
    region = pymupdf.Rect(54, model.y0 - 30, page.rect.width - 54, model.y1 + 40)
    assert grid(page, region, "Table 2") == [
        ["Model", "Acc.", "F1"],
        ["BERT-base", "84.6", "0.812"],
        ["RoBERTa", "86.1", "0.829"],
        ["Ours", "88.0", "0.851"],
    ]


def test_stacked_tables_with_captions_below_are_kept_apart(tmp_path: Path) -> None:
    html = f"""<p>{FILLER}</p>
    <table><tr><th>System</th><th>Dev</th><th>Test</th></tr>
    <tr><td>Human</td><td>86.3</td><td>86.9</td></tr>
    <tr><td>Ours</td><td>78.7</td><td>80.0</td></tr></table>
    <p class="caption">Table 2: SQuAD 1.1 results.</p>
    <table><tr><th>System</th><th>EM</th><th>F1</th></tr>
    <tr><td>unet</td><td>71.4</td><td>74.9</td></tr>
    <tr><td>BERT</td><td>80.0</td><td>83.1</td></tr></table>
    <p class="caption">Table 3: SQuAD 2.0 results.</p><p>{FILLER}</p>"""
    page = pdf(tmp_path, html)[0]
    both = rect_of(page, "Human") | rect_of(page, "unet")
    region = pymupdf.Rect(54, both.y0 - 10, 558, both.y1 + 10)  # covers both tables
    assert grid(page, region, "Table 2") == [
        ["System", "Dev", "Test"],
        ["Human", "86.3", "86.9"],
        ["Ours", "78.7", "80.0"],
    ]
    assert grid(page, region, "Table 3") == [
        ["System", "EM", "F1"],
        ["unet", "71.4", "74.9"],
        ["BERT", "80.0", "83.1"],
    ]


def test_caption_above_table_with_text_around(tmp_path: Path) -> None:
    html = f"""<p>{FILLER * 2}</p>
    <p class="caption">Table 4: Results with the caption above, as in NeurIPS papers.</p>
    {TABLE_A}
    <p>{FILLER * 2}</p>"""
    page = pdf(tmp_path, html)[0]
    region = rect_of(page, "BERT-base") | rect_of(page, "0.851")
    assert grid(page, region, "Table 4")[0] == ["Model", "Acc.", "F1"]
    assert len(grid(page, region, "Table 4")) == 4


def test_tight_numeric_columns_are_split(tmp_path: Path) -> None:
    head = "".join(f"<th>c{i}</th>" for i in range(10))
    rows = "".join(
        "<tr><td>run"
        + str(r)
        + "</td>"
        + "".join(f"<td>{70 + r + i / 10:.1f}</td>" for i in range(10))
        + "</tr>"
        for r in range(4)
    )
    html = f"<style>{TIGHT_CSS}</style><table><tr><th>name</th>{head}</tr>{rows}</table>"
    html += '<p class="caption">Table 9: Tight table.</p>'
    page = pdf(tmp_path, html)[0]
    g = grid(page, rect_of(page, "run0") | rect_of(page, "run3"), "Table 9")
    assert len(g[0]) == 11
    assert g[1] == ["run0"] + [f"{70 + i / 10:.1f}" for i in range(10)]


def test_long_label_row_does_not_merge_columns(tmp_path: Path) -> None:
    html = """<table>
    <tr><th>Method</th><th>Top 1</th><th>Top 5</th></tr>
    <tr><td colspan="3">Methods using other architectures and much longer labels:</td></tr>
    <tr><td>Rotation</td><td>55.4</td><td>-</td></tr>
    <tr><td>BigBiGAN</td><td>61.3</td><td>81.9</td></tr>
    <tr><td>SimCLR</td><td>74.2</td><td>92.0</td></tr>
    </table><p class="caption">Table 6: Linear evaluation.</p>"""
    page = pdf(tmp_path, html)[0]
    g = grid(page, rect_of(page, "Rotation") | rect_of(page, "92.0"), "Table 6")
    assert len(g[0]) == 3
    assert g[-1] == ["SimCLR", "74.2", "92.0"]
    assert g[1][0].startswith("Methods using other architectures")


def test_superscript_exponents_are_kept(tmp_path: Path) -> None:
    html = """<table>
    <tr><th>Model</th><th>BLEU</th><th>Cost</th></tr>
    <tr><td>GNMT</td><td>24.6</td><td>2.3 · 10<sup>19</sup></td></tr>
    <tr><td>Transformer</td><td>27.3</td><td>3.3 · 10<sup>18</sup></td></tr>
    </table><p class="caption">Table 2: Cost.</p>"""
    page = pdf(tmp_path, html)[0]
    result = reconstruct_table(page, rect_of(page, "GNMT") | rect_of(page, "27.3"), label="Table 2")
    assert result is not None
    table, _ = result
    cost = [c for c in table.cells if c.col == 2 and c.row > 0]
    assert [c.text for c in cost] == ["2.3 · 10^19", "3.3 · 10^18"]
    assert cost[0].value == pytest.approx(2.3e19)


def test_prose_region_gives_no_grid(tmp_path: Path) -> None:
    page = pdf(tmp_path, f"<p>{FILLER * 6}</p>")[0]
    region = pymupdf.Rect(54, 100, 558, 300)
    assert reconstruct_table(page, region, label="Table 1") is None
