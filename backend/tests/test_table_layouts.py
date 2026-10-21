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
    # Realistic spacing: a caption sits closer to its own table than to the next one.
    html = f"""<p>{FILLER}</p>
    <table><tr><th>System</th><th>Dev</th><th>Test</th></tr>
    <tr><td>Human</td><td>86.3</td><td>86.9</td></tr>
    <tr><td>Ours</td><td>78.7</td><td>80.0</td></tr></table>
    <p class="caption" style="margin-top:2pt; margin-bottom:16pt">Table 2: SQuAD 1.1 results.</p>
    <table><tr><th>System</th><th>EM</th><th>F1</th></tr>
    <tr><td>unet</td><td>71.4</td><td>74.9</td></tr>
    <tr><td>BERT</td><td>80.0</td><td>83.1</td></tr></table>
    <p class="caption" style="margin-top:2pt; margin-bottom:16pt">Table 3: SQuAD 2.0 results.</p>
    <p>{FILLER}</p>"""
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


# ---- behaviours added after running the 10 arXiv papers -------------------------------------


def test_zero_height_rules_are_found_and_tell_the_caption_side(tmp_path: Path) -> None:
    from app.pipeline.parse.tables import _caption_side, _horizontal_rules

    doc = pymupdf.open()
    page = doc.new_page()
    # booktabs rules are zero-height lines; PyMuPDF treats those rects as empty
    page.draw_line((100, 200), (400, 200))
    rules = _horizontal_rules(page, page.rect)
    assert len(rules) == 1
    below_rule = pymupdf.Rect(150, 210, 350, 220)  # caption 10 pt under the table's last rule
    assert _caption_side(rules, below_rule, 500) == "above"
    above_rule = pymupdf.Rect(150, 180, 350, 190)
    assert _caption_side(rules, above_rule, 500) == "below"


def test_short_centred_caption_on_two_column_page_means_full_width(tmp_path: Path) -> None:
    from app.pipeline.parse.tables import _column_bounds

    page = pdf(tmp_path, f"<p>{FILLER * 12}</p>", columns=2)[0]
    width = page.rect.width
    centred = pymupdf.Rect(width / 2 - 80, 300, width / 2 + 80, 310)
    assert _column_bounds(page, centred, centred) == (0.0, width)
    right_col = pymupdf.Rect(width / 2 + 20, 300, width - 60, 310)
    assert _column_bounds(page, right_col, right_col)[0] > width / 2 - 10


def test_caption_is_found_on_another_page_than_reported(tmp_path: Path) -> None:
    from app.pipeline.parse.tables import locate_caption

    html = f"<p>{FILLER * 45}</p>{TABLE_A}<p class='caption'>Table 5: Late table.</p>"
    doc = pdf(tmp_path, html)
    assert doc.page_count >= 2
    located = locate_caption(doc, "Table 5", hint_page=1)
    assert located is not None and located[0] == doc.page_count
    # "Table 5 shows ..." in running text is not a caption
    assert locate_caption(pdf(tmp_path, "<p>Table 5 shows results.</p>", name="b.pdf"),
                          "Table 5", 1) is None  # fmt: skip


def test_thin_space_thousands_and_dash_cells(tmp_path: Path) -> None:
    html = """<table>
    <tr><th>Dataset</th><th>Steps</th><th>Dev</th><th>Test</th></tr>
    <tr><td>ImageNet</td><td>20&#8201;000</td><td>-</td><td>82.3</td></tr>
    <tr><td>CIFAR</td><td>2&#8201;500</td><td>85.6</td><td>-</td></tr>
    </table><p class="caption">Table 4: Steps.</p>"""
    page = pdf(tmp_path, html)[0]
    g = grid(page, rect_of(page, "ImageNet") | rect_of(page, "CIFAR"), "Table 4")
    assert g[1] == ["ImageNet", "20000", "-", "82.3"]  # not "-82.3", not two step columns
    assert g[2] == ["CIFAR", "2500", "85.6", "-"]


def test_running_head_is_not_part_of_the_table(tmp_path: Path) -> None:
    html = f"{TABLE_A}<p class='caption'>Table 1: Head.</p><p>{FILLER * 45}</p>"
    out = tmp_path / "heads.pdf"
    render(html, out)
    doc = pymupdf.open(out)
    for i in range(doc.page_count):  # the same running head on every page, above the text
        p = doc[i]
        p.insert_text((200, 60), "A Framework For Testing Running Heads", fontsize=9)
    doc.save(tmp_path / "heads2.pdf")
    page = pymupdf.open(tmp_path / "heads2.pdf")[0]
    g = grid(page, rect_of(page, "BERT-base") | rect_of(page, "0.851"), "Table 1")
    assert g[0] == ["Model", "Acc.", "F1"]


def test_caption_label_from_text() -> None:
    from app.pipeline.parse.tables import caption_label

    assert caption_label("TableB.5. Comparison of transfer") == "Table B.5"
    assert caption_label("Table 3: SQuAD 2.0 results.") == "Table 3"
    assert caption_label("Table 2 shows the results") is None


def test_table_of_formulas_without_numbers(tmp_path: Path) -> None:
    html = """<table>
    <tr><th>Layer Type</th><th>Complexity</th><th>Sequential</th><th>Path Length</th></tr>
    <tr><td>Self-Attention</td><td>O(n^2 d)</td><td>O(1)</td><td>O(1)</td></tr>
    <tr><td>Recurrent</td><td>O(n d^2)</td><td>O(n)</td><td>O(n)</td></tr>
    </table><p class="caption">Table 1: Complexity.</p>"""
    page = pdf(tmp_path, html)[0]
    g = grid(page, rect_of(page, "Recurrent"), "Table 1")
    assert g[1] == ["Self-Attention", "O(n^2 d)", "O(1)", "O(1)"]


def test_caption_tail_with_numbers_is_not_a_table_row(tmp_path: Path) -> None:
    html = f"""<p>{FILLER}</p>
    <p class="caption" style="margin-bottom:14pt">Figure 3: Training curves.
    Right: ResNets with 110 and 1202 layers.</p>
    {TABLE_A}<p class="caption">Table 7: Detection.</p>"""
    page = pdf(tmp_path, html)[0]
    g = grid(page, rect_of(page, "BERT-base") | rect_of(page, "0.851"), "Table 7")
    assert g[0] == ["Model", "Acc.", "F1"]
