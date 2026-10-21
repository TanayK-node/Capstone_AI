import random
from pathlib import Path

import pytest

from app.config import Settings
from app.llm.cache import MemoryCache
from app.llm.client import LLMClient
from app.pipeline.parse.grobid import parse_with_tei
from app.pipeline.structure.roles import classify_heading
from app.pipeline.structure.sections import structure_document
from app.schemas.document import Block, PageInfo, ParsedDocument
from tests.conftest import FakeClock, FakeProvider

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize(
    ("heading", "role"),
    [
        ("1 Introduction", "introduction"),
        ("2. Related Work", "related_work"),
        ("3 Preliminaries", "background"),
        ("3 Our Approach", "method"),
        ("4 Model Architecture", "method"),
        ("5 Experimental Setup", "experiments"),
        ("5.2 Datasets", "experiments"),
        ("6 Results", "results"),
        ("6 Experimental Results", "results"),
        ("6.3 Ablation Studies", "ablation"),
        ("7 Discussion", "discussion"),
        ("Limitations", "limitations"),
        ("8 Conclusion and Future Work", "conclusion"),
        ("Acknowledgments", "acknowledgements"),
        ("References", "references"),
        ("Appendix", "appendix"),
        ("Why Does It Work?", None),
    ],
)
def test_classify_heading(heading: str, role: str | None) -> None:
    assert classify_heading(heading) == role


def test_fixture_roles_and_chunk_hierarchy() -> None:
    doc = parse_with_tei(
        FIXTURES / "paper_single.pdf", (FIXTURES / "paper_single.tei.xml").read_bytes()
    )
    result = structure_document(doc, client=None)
    roles = {s.title: (s.role, s.role_source) for s in result.sections}
    assert roles["3 Method"] == ("method", "rule")
    assert roles["3.1 Training details"] == ("method", "inherited")
    assert roles["4.1 Ablation study"] == ("ablation", "rule")
    assert result.llm_prompt_version is None  # every heading resolved by rules

    chunks = {c.id: c for c in result.chunks}
    sentence = next(c for c in result.chunks if c.level == "sentence")
    paragraph = chunks[sentence.parent_id or ""]
    section = chunks[paragraph.parent_id or ""]
    assert (paragraph.level, section.level) == ("paragraph", "section")
    assert sentence.boxes and sentence.boxes[0].page >= 1
    table_chunk = next(c for c in result.chunks if c.text.startswith("Table 1"))
    assert "SparseRoute (ours) | 26.4 ± 0.2" in table_chunk.text


def _doc(headings: list[str]) -> ParsedDocument:
    blocks: list[Block] = []
    for h in headings:
        for kind, text in (("heading", h), ("paragraph", f"Text under {h}.")):
            blocks.append(
                Block(
                    id=f"b{len(blocks):04d}",
                    type=kind,
                    order=len(blocks),
                    page=1,
                    bbox=None,
                    section_path=[h],
                    text=text,
                )
            )
    return ParsedDocument(
        parser="test",
        parser_version="0",
        pages=[PageInfo(number=1, width=1, height=1)],
        blocks=blocks,
    )


def test_unknown_headings_go_to_one_llm_call(settings: Settings, clock: FakeClock) -> None:
    provider = FakeProvider("gemini", ['{"sections": [{"index": 0, "role": "method"}]}'])
    llm = LLMClient(
        settings,
        {"gemini": provider},
        MemoryCache(),
        clock=clock,
        sleep=clock.sleep,
        rng=random.Random(0),
    )
    doc = _doc(["1 Introduction", "2 Sparse Routing", "References", "Proofs"])
    result = structure_document(doc, llm)
    roles = {s.title: (s.role, s.role_source) for s in result.sections}
    assert roles["2 Sparse Routing"] == ("method", "llm")
    assert roles["Proofs"] == ("appendix", "rule")  # after References
    assert len(provider.calls) == 1
    assert result.llm_prompt_version == "section_roles@1"


def test_llm_failure_leaves_role_other(settings: Settings, clock: FakeClock) -> None:
    result = structure_document(_doc(["2 Sparse Routing"]), client=None)
    assert result.sections[0].role == "other"
    assert result.warnings == ["section '2 Sparse Routing': role unknown"]
