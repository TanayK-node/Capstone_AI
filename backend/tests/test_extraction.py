"""Extraction + grounding on the fixture paper with a fake LLM (no network)."""

import random
from pathlib import Path

from app.config import Settings
from app.llm.cache import MemoryCache
from app.llm.client import LLMClient
from app.pipeline.extract.extractor import extract_document
from app.pipeline.parse.grobid import parse_with_tei
from app.pipeline.structure.sections import structure_document
from app.pipeline.verify.grounding import ground, grounding_score, locate, normalize
from app.schemas.document import ParsedDocument
from tests.conftest import FakeClock
from tests.fake_llm import FakePaperProvider

FIXTURES = Path(__file__).parent / "fixtures"
PDF = FIXTURES / "paper_single.pdf"


def fixture_doc() -> ParsedDocument:
    doc = parse_with_tei(PDF, (FIXTURES / "paper_single.tei.xml").read_bytes())
    roles = structure_document(doc, client=None).block_roles
    for block in doc.blocks:
        block.role = roles.get(block.id)
    return doc


def client(settings: Settings, provider: FakePaperProvider) -> LLMClient:
    clock = FakeClock()
    return LLMClient(settings, {"gemini": provider}, MemoryCache(), clock=clock,
                     sleep=clock.sleep, rng=random.Random(0))  # fmt: skip


def test_extraction_groups_and_rule_items(settings: Settings) -> None:
    provider = FakePaperProvider()
    run = extract_document(fixture_doc(), client(settings, provider))
    ex = run.extraction
    assert [g.status for g in run.groups] == ["done", "done", "done", "done"]
    assert len(provider.calls) == 4  # one call per section group
    assert "Our contributions are threefold" in ex.contributions[0].evidence[0].quote
    hp = ex.hyperparameters[0]
    assert hp.value_raw == "3e-4" and hp.value_norm == 3e-4  # normalised in Python
    assert [u.value for u in ex.code_urls] == ["https://github.com/example/sparseroute"]
    assert ex.code_urls[0].source == "rule"
    assert ex.metadata.title == "Sparse Routing Improves Low-Resource Translation"
    # The experiments prompt carries the regex hints.
    experiments = next(c for c in provider.calls if "experimental setup" in c.prompt)
    assert "Hints found by pattern matching" in experiments.prompt
    assert {i.id for _, i in ex.all_items()} == {
        f"{n}.{k}" for n, i in ex.all_items() for k in [int(i.id.rsplit(".", 1)[1])]
    }


def test_grounding_locates_quotes_and_flags_invented_ones(settings: Settings) -> None:
    doc = fixture_doc()
    provider = FakePaperProvider(invented_quote_for="limitations")
    llm = client(settings, provider)
    ex = extract_document(doc, llm).extraction
    run = ground(ex, doc, llm, PDF)

    contrib = ex.contributions[0].evidence[0]
    assert contrib.grounding_status == "verified"
    assert contrib.boxes and contrib.bbox is not None and contrib.page == 1
    # Sentence-level boxes: the highlight is the quoted sentence, not the whole paragraph.
    block = next(b for b in doc.blocks if b.id == contrib.chunk_id)
    assert sum(b.area for b in contrib.boxes) < sum(b.area for b in block.boxes)

    invented = ex.limitations[0].evidence[0]
    assert invented.grounding_status == "unlocated" and invented.boxes == []
    assert run.unlocated >= 1 and run.support_calls == 1
    assert ex.code_urls[0].evidence[0].grounding_status == "verified"
    assert 0 < grounding_score(ex) < 1


def test_locate_tolerates_hyphenation_ligatures_and_wrong_chunk() -> None:
    doc = fixture_doc()
    blocks = {b.id: b for b in doc.blocks}
    target = next(b for b in doc.blocks if b.text.startswith("We train with Adam"))
    quote = "We train with Adam using a learning rate of 3e-4, batch size 256 and 50k steps"
    match = locate(quote, cited="b0000", blocks=blocks)  # wrong chunk cited
    assert match is not None and match.block.id == target.id
    assert normalize("repre- sentation of ﬁne-tuning") == "representation of fine-tuning"


def test_no_llm_leaves_support_unchecked(settings: Settings) -> None:
    doc = fixture_doc()
    ex = extract_document(doc, client(settings, FakePaperProvider())).extraction
    run = ground(ex, doc, None, PDF)
    statuses = {
        e.grounding_status for _, i in ex.all_items() for e in i.evidence if i.source == "llm"
    }
    assert statuses <= {"unchecked", "unlocated"}
    assert run.warnings
