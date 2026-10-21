"""Parsers on the fixture PDFs. GROBID output is replayed from the committed TEI files, so these
tests need no running GROBID."""

from pathlib import Path

import pytest

from app.pipeline.parse.grobid import parse_with_tei
from app.pipeline.parse.pymupdf_parser import PyMuPDFParser
from app.pipeline.parse.tei import parse_coords
from app.schemas.document import ParsedDocument

FIXTURES = Path(__file__).parent / "fixtures"


def grobid_doc(name: str) -> ParsedDocument:
    return parse_with_tei(FIXTURES / f"{name}.pdf", (FIXTURES / f"{name}.tei.xml").read_bytes())


def headings(doc: ParsedDocument) -> list[str]:
    return [b.text for b in doc.blocks if b.type == "heading"]


def test_parse_coords_dedupes_and_converts_to_corners() -> None:
    boxes = parse_coords("1,10,20,30,5;1,10,20,30,5;2,0,0,1,1")
    assert [(b.page, b.x0, b.y0, b.x1, b.y1) for b in boxes] == [
        (1, 10, 20, 40, 25),
        (2, 0, 0, 1, 1),
    ]


def test_grobid_single_column_structure() -> None:
    doc = grobid_doc("paper_single")
    assert doc.metadata.title == "Sparse Routing Improves Low-Resource Translation"
    assert [a.name for a in doc.metadata.authors] == ["Asha Rao", "Daniel Okafor"]
    assert doc.metadata.abstract and doc.metadata.abstract.startswith("We introduce SparseRoute")
    assert headings(doc) == [
        "1 Introduction",
        "2 Related Work",
        "3 Method",
        "3.1 Training details",
        "4 Experiments",
        "4.1 Ablation study",
        "5 Limitations",
        "6 Conclusion",
    ]
    training = next(b for b in doc.blocks if b.text.startswith("We train with Adam"))
    assert training.section_path == ["3 Method", "3.1 Training details"]
    assert len(training.sentences) == 3
    assert all(s.boxes for s in training.sentences)
    assert [b.type for b in doc.blocks].count("equation") == 1
    assert len(doc.references) == 3
    assert doc.references[2].arxiv_id == "2207.04672"


def test_grobid_table_is_rebuilt_and_placed_in_its_section() -> None:
    doc = grobid_doc("paper_single")
    (table,) = doc.tables
    assert table.label == "Table 1"
    assert table.section_path == ["4 Experiments"]
    assert table.table is not None and table.table.n_rows == 4 and table.table.n_cols == 4
    assert table.bbox is not None and table.bbox.page == 2


def test_grobid_two_column_table_header_does_not_become_headings() -> None:
    doc = grobid_doc("paper_twocol")
    assert doc.metadata.title == "Contrastive Pretraining for Natural Language Inference"
    assert "Model" not in headings(doc)
    assert all(not b.text.startswith("BERT") for b in doc.blocks if b.type == "paragraph")
    (table,) = doc.tables
    assert table.section_path == ["3 Results"]
    assert table.table is not None and table.table.grid()[0] == ["Model", "Acc. (%)", "F1"]


@pytest.mark.parametrize("name", ["paper_single", "paper_twocol"])
def test_block_ids_and_order_are_sequential(name: str) -> None:
    doc = grobid_doc(name)
    assert [b.order for b in doc.blocks] == list(range(len(doc.blocks)))
    assert len({b.id for b in doc.blocks}) == len(doc.blocks)


def test_pymupdf_parser_single_column() -> None:
    doc = PyMuPDFParser().parse(FIXTURES / "paper_single.pdf")
    assert doc.parser == "pymupdf"
    assert doc.metadata.title == "Sparse Routing Improves Low-Resource Translation"
    assert headings(doc) == [
        "Abstract",
        "1 Introduction",
        "2 Related Work",
        "3 Method",
        "3.1 Training details",
        "4 Experiments",
        "4.1 Ablation study",
        "5 Limitations",
        "6 Conclusion",
        "References",
    ]
    assert len(doc.references) == 3  # wrapped reference lines merged back
    (table,) = doc.tables
    assert table.table is not None and table.table.n_rows == 4
    assert table.section_path == ["4 Experiments"]
    # The caption is part of the table block, not a separate figure.
    assert not [b for b in doc.blocks if b.type == "figure"]


def test_pymupdf_parser_two_column_reading_order() -> None:
    doc = PyMuPDFParser().parse(FIXTURES / "paper_twocol.pdf")
    order = headings(doc)
    assert order.index("1 Introduction") < order.index("2 Approach") < order.index("3 Results")
    assert order.index("3 Results") < order.index("4 Conclusion")
    authors = next(b for b in doc.blocks if b.text == "Mei Lin, Tomas Varga")
    assert authors.section_path == []  # front matter, not abstract


def test_notice_merged_into_title_is_dropped() -> None:
    from app.pipeline.parse.tei import clean_title

    merged = (
        "Provided proper attribution is provided, Google hereby grants permission to reproduce "
        "the tables and figures in this paper solely for use in journalistic or scholarly "
        "works. Attention Is All You Need"
    )
    assert clean_title(merged) == "Attention Is All You Need"
    assert clean_title("BERT: Pre-training of Deep Bidirectional Transformers") == (
        "BERT: Pre-training of Deep Bidirectional Transformers"
    )
    assert clean_title("Mr. Smith Goes to Washington") == "Mr. Smith Goes to Washington"
