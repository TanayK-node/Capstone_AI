"""Citation graph and novelty positioning (M12)."""

from __future__ import annotations

import json
from typing import Any

import httpx
from lxml import etree

from app.config import Settings
from app.pipeline.context.graph import build_report
from app.pipeline.context.s2 import S2Client
from app.pipeline.parse.tei import _cites
from app.schemas.document import ParsedDocument
from tests.fake_llm import FakePaperProvider
from tests.test_extraction import PDF, client, fixture_doc


def test_in_text_citations_from_tei() -> None:
    s = etree.fromstring(
        '<s xmlns="http://www.tei-c.org/ns/1.0">As in <ref type="bibr" target="#b3">[4,</ref>'
        '<ref type="bibr" target="#b0">1]</ref> and <ref type="bibr">[9]</ref>, see '
        '<ref type="figure" target="#fig_1">Fig. 2</ref> and <ref type="bibr" target="#b3">'
        "[4]</ref>.</s>"
    )
    assert _cites(s) == ["b3", "b0"]  # resolved only, in order, once each


def cited_doc() -> ParsedDocument:
    """The fixture paper, citing b0 (Attention) twice and b1 (Switch) once."""
    doc = fixture_doc()
    paras = [b for b in doc.blocks if b.type == "paragraph" and b.sentences]
    paras[1].sentences[0].cites = ["b0"]
    paras[3].sentences[0].cites = ["b0", "b1"]
    doc.references[0].arxiv_id = "1706.03762v7"
    return doc


S2_PAPER = {"paperId": "P", "title": "SparseRoute", "year": 2024, "venue": "ICML",
            "citationCount": 120, "influentialCitationCount": 9, "referenceCount": 4,
            "authors": [{"name": "A. Author"}], "url": "https://s2/P"}  # fmt: skip
S2_REFS = [
    {"isInfluential": True, "citedPaper": {
        "paperId": "R0", "title": "Attention Is All You Need", "year": 2017,
        "externalIds": {"ArXiv": "1706.03762"}, "citationCount": 100000,
        "abstract": "The dominant sequence transduction models are based on recurrence."}},
    {"isInfluential": False, "citedPaper": {
        "paperId": "R1", "title": "Switch Transformers: Scaling to Trillion Parameter Models "
        "with Simple and Efficient Sparsity", "year": 2021, "citationCount": 2000,
        "abstract": "Mixture of experts models select different parameters per input."}},
    {"isInfluential": False, "citedPaper": {
        "paperId": "R9", "title": "Adam: A Method for Stochastic Optimization",
        "citationCount": 150000, "abstract": "An optimizer."}},
    {"isInfluential": False, "citedPaper": {"paperId": "RX", "title": None}},
]  # fmt: skip
S2_CITES = [
    {"isInfluential": infl, "citingPaper": {"paperId": pid, "title": t, "citationCount": n}}
    for infl, pid, t, n in [(False, "C1", "Big", 900), (True, "C2", "Infl", 5),
                            (False, "C3", "Small", 1)]
]  # fmt: skip


def fake_s2(calls: list[str], *, busy: int = 0) -> S2Client:
    state = {"busy": busy}

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        if state["busy"]:
            state["busy"] -= 1
            return httpx.Response(429, headers={"Retry-After": "1"})
        path = request.url.path.removeprefix("/graph/v1")
        if path == "/paper/arXiv:2401.00001":
            return httpx.Response(404)
        if path == "/paper/search/match":
            return httpx.Response(200, json={"data": [S2_PAPER]})
        body: dict[str, Any] = {
            "/paper/P/references": {"data": S2_REFS},
            "/paper/P/citations": {"data": S2_CITES},
        }.get(path, {})
        return httpx.Response(200 if body else 404, json=body)

    return S2Client(transport=httpx.MockTransport(handler), sleep=lambda s: None)


def test_s2_retries_when_busy_then_finds_by_title() -> None:
    calls: list[str] = []
    s2 = fake_s2(calls, busy=2)
    found = s2.find(arxiv_id="2401.00001", doi=None, s2_id=None, title="SparseRoute: routing")
    assert found is not None and found["paperId"] == "P"
    assert calls[:3] == ["/graph/v1/paper/arXiv:2401.00001"] * 3  # two 429s, then a 404
    assert calls[-1] == "/graph/v1/paper/search/match"
    assert len(s2.references("P")) == 3  # the record without a title is dropped


def test_graph_with_semantic_scholar_and_grounded_novelty(settings: Settings) -> None:
    doc = cited_doc()
    llm = client(settings, FakePaperProvider())
    run = build_report(doc, {"title": "SparseRoute", "arxiv_id": "2401.00001"},
                       s2=fake_s2([]), client=llm, extraction=None, pdf_path=PDF)  # fmt: skip
    r = run.report
    assert r.source == "semantic_scholar" and r.citation_count == 120
    # Matched by arXiv id (b0) and by title (b1); most cited in the text first.
    top = r.references[0]
    assert (top.ref_id, top.mentions, top.influential) == ("b0", 2, True)
    assert top.citation_count == 100000 and len(top.evidence) == 2
    assert top.evidence[0].grounding_status == "verified" and top.evidence[0].boxes
    assert r.references[1].ref_id == "b1" and r.references[1].citation_count == 2000
    # Adam is not in the PDF's list (GROBID missed it): kept, from S2, never cited in text.
    adam = next(n for n in r.references if n.title.startswith("Adam"))
    assert adam.id == "s2:R9" and adam.mentions == 0 and adam.ref_id is None
    assert r.reference_count == 4  # 3 PDF entries + Adam
    assert [c.title for c in r.citations] == ["Infl", "Big", "Small"]  # influential first

    novelty = r.novelty
    assert novelty is not None and novelty.summary
    by_node = {p.node: p for p in novelty.positions}
    assert set(by_node) == {"ref:b0", "ref:b1"}  # R99 named nothing: dropped
    assert by_node["ref:b0"].evidence[0].grounding_status == "verified"
    assert by_node["ref:b1"].evidence[0].grounding_status == "unlocated"  # kept, flagged
    assert any("unknown reference" in w for w in run.warnings)
    prompt = llm.providers["gemini"].calls[-1].prompt  # type: ignore[attr-defined]
    assert "[R1] Attention Is All You Need" in prompt and "Adam" in prompt


def test_graph_without_semantic_scholar(settings: Settings) -> None:
    run = build_report(cited_doc(), {"title": "SparseRoute"}, s2=None,
                       client=client(settings, FakePaperProvider()), extraction=None,
                       pdf_path=PDF)  # fmt: skip
    r = run.report
    assert r.source == "pdf" and r.citations == [] and r.novelty is None
    assert [n.ref_id for n in r.references] == ["b0", "b1", "b2"]
    assert r.references[0].url == "https://arxiv.org/abs/1706.03762v7"
    assert any("no novelty summary" in w for w in run.warnings)
    json.dumps(r.model_dump(mode="json"))  # storable
