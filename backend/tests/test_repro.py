"""Reproducibility analyzer (M6): rules, GitHub checks (mocked HTTP), LLM fill-in, scoring."""

import json
import random

import httpx
import pytest

from app.config import Settings
from app.llm.cache import MemoryCache
from app.llm.client import LLMClient
from app.pipeline.extract.extractor import extract_document
from app.pipeline.repro.analyzer import analyze, score_card
from app.pipeline.repro.checklist import load_checklist
from app.pipeline.repro.github import GitHubClient, parse_repo_url
from app.pipeline.repro.rules import RULES
from app.pipeline.verify.grounding import ground
from app.schemas.repro import ItemResult, Scorecard
from tests.conftest import FakeClock
from tests.fake_llm import FakePaperProvider
from tests.test_extraction import PDF, fixture_doc

README = """# SparseRoute
## Installation
pip install -r requirements.txt
## Training
python train.py --config configs/flores.yaml
## Evaluation
python evaluate.py --checkpoint ckpt/best.pt
Pretrained checkpoints are on the release page.
"""


def github_transport(
    repo: dict | None = None, files: list[str] | None = None
) -> httpx.MockTransport:  # type: ignore[type-arg]
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if repo is None:
            return httpx.Response(404, json={"message": "Not Found"})
        if path.endswith("/contents"):
            return httpx.Response(200, json=[{"name": f} for f in files or []])
        if path.endswith("/readme"):
            return httpx.Response(200, text=README)
        return httpx.Response(200, json=repo)

    return httpx.MockTransport(handler)


REPO = {
    "name": "sparseroute",
    "owner": {"login": "example"},
    "license": {"spdx_id": "MIT", "name": "MIT License"},
    "stargazers_count": 42,
    "pushed_at": "2026-01-02T00:00:00Z",
    "archived": False,
}


def llm(settings: Settings, provider: FakePaperProvider) -> LLMClient:
    clock = FakeClock()
    return LLMClient(settings, {"gemini": provider}, MemoryCache(), clock=clock,  # type: ignore[dict-item]
                     sleep=clock.sleep, rng=random.Random(0))  # fmt: skip


def run_fixture(settings: Settings, provider: FakePaperProvider, github: GitHubClient | None):  # type: ignore[no-untyped-def]
    doc = fixture_doc()
    client = llm(settings, provider)
    extraction = extract_document(doc, client).extraction
    ground(extraction, doc, client, PDF)
    return analyze(doc, extraction, load_checklist(), client=client, github=github, pdf_path=PDF)


# ------------------------------------------------------------------ config


def test_checklist_rules_exist_and_items_have_questions() -> None:
    checklist = load_checklist()
    assert len(checklist.items) == 21
    assert {i.rule for i in checklist.items if i.rule} <= set(RULES)
    assert all(i.question for i in checklist.items)
    assert len({i.id for i in checklist.items}) == len(checklist.items)


# ------------------------------------------------------------------ scoring


def test_score_is_weighted_and_skips_unknown_and_not_applicable() -> None:
    checklist = load_checklist()
    status = {"code_url": "present", "repo_reachable": "partial", "license": "unknown",
              "dependency_file": "not_applicable"}  # fmt: skip
    items = [
        ItemResult(id=i.id, group=i.group, description=i.description, weight=i.weight,
                   status=status.get(i.id, "missing"))  # type: ignore[arg-type]
        for i in checklist.items
    ]  # fmt: skip
    card = Scorecard(checklist_version=checklist.version, score=None, groups=[], items=items)
    score_card(card, checklist)
    code = next(g for g in card.groups if g.id == "code")
    # code_url (w2) present = 2, repo_reachable (w1) partial = 0.5, run_instructions and
    # pretrained_weights (w1 each) missing = 0; license / dependency_file left out.
    assert code.score == round(2.5 / 5, 3)
    # Every other group is all missing: total = 0.25 * 0.5 / (sum of group weights) * 100
    assert card.score == round(100 * 0.25 * 0.5 / 1.0, 1)
    # Missing before partial; heaviest first (item weight x group weight: 2 x 0.25 setup).
    assert card.missing[0] == "hyperparameters_all"
    assert "repo_reachable" in card.missing and "license" not in card.missing
    assert len(card.questions) == len(card.missing)


# ------------------------------------------------------------------ GitHub


def test_parse_repo_url() -> None:
    info = parse_repo_url("https://github.com/example/sparse-route.git/tree/main/src")
    assert (info.host, info.owner, info.name) == ("github.com", "example", "sparse-route")
    assert parse_repo_url("https://huggingface.co/org/model").host == "huggingface.co"


def test_github_client_reads_metadata_files_and_readme() -> None:
    gh = GitHubClient(transport=github_transport(REPO, ["README.md", "requirements.txt"]))
    info = gh.inspect("https://github.com/example/sparseroute")
    assert info.reachable and info.license == "MIT" and info.stars == 42
    assert info.root_files == ["README.md", "requirements.txt"]
    assert "python train.py" in info.readme_excerpt
    missing = GitHubClient(transport=github_transport(None)).inspect("https://github.com/a/b")
    assert missing.reachable is False


# ------------------------------------------------------------------ end to end


def test_analyzer_on_fixture_paper(settings: Settings) -> None:
    provider = FakePaperProvider()
    gh = GitHubClient(transport=github_transport(REPO, ["requirements.txt"]))
    run = run_fixture(settings, provider, gh)
    items = {i.id: i for i in run.scorecard.items}

    # Rules decide from the paper text, with grounded (highlightable) evidence.
    for item_id in ("training_details", "hardware", "training_time", "runs_seeds", "error_bars"):
        assert items[item_id].status == "present" and items[item_id].source == "rule", item_id
        ev = items[item_id].evidence[0]
        assert ev.grounding_status == "verified" and ev.boxes, item_id
    assert items["code_url"].status == "present"
    assert items["datasets_access"].source == "extraction"
    # Repository facts come from the (mocked) GitHub API.
    assert items["license"].status == "present" and "MIT" in items["license"].note
    assert items["dependency_file"].status == "present"
    assert items["run_instructions"].status == "present"
    assert items["pretrained_weights"].source == "repo"

    # Only undecided items went to the LLM, in one call.
    checklist_calls = [c for c in provider.calls if "Checklist items:" in c.prompt]
    assert len(checklist_calls) == 1
    asked = checklist_calls[0].prompt.split("Checklist items:")[1].split("Paper text:")[0]
    assert "- datasets_named:" in asked and "- hardware:" not in asked
    assert items["datasets_named"].source == "llm"
    assert items["datasets_named"].evidence[0].grounding_status == "verified"
    assert items["memory"].status == "missing" and items["memory"].question

    card = run.scorecard
    assert card.score is not None and 0 < card.score < 100
    assert card.repo is not None and card.repo.reachable


def test_llm_claim_with_invented_quote_is_capped_at_partial(settings: Settings) -> None:
    provider = FakePaperProvider(repro_invented="significance")
    run = run_fixture(settings, provider, None)
    item = next(i for i in run.scorecard.items if i.id == "significance")
    assert item.status == "partial"
    assert item.evidence[0].grounding_status == "unlocated"
    assert "not confirmed" in item.note


def test_without_github_check_repo_items_are_unknown(settings: Settings) -> None:
    run = run_fixture(settings, FakePaperProvider(), None)
    items = {i.id: i for i in run.scorecard.items}
    assert items["license"].status == "unknown"
    assert "license" not in run.scorecard.missing  # unknown is not counted as missing
    assert any("switched off" in w for w in run.scorecard.warnings)


@pytest.mark.parametrize("fmt", ["md", "json", "csv"])
def test_scorecard_in_exports(settings: Settings, fmt: str) -> None:
    from app.pipeline import export

    doc = fixture_doc()
    client = llm(settings, FakePaperProvider())
    extraction = extract_document(doc, client).extraction
    card = analyze(doc, extraction, load_checklist(), client=client, github=None).scorecard
    body = export.render(extraction, fmt, card)
    if fmt == "md":
        assert "## Reproducibility:" in body and "Questions for the authors" in body
    elif fmt == "json":
        assert json.loads(body)["reproducibility"]["checklist_version"] == 2
    else:
        assert "checklist:compute,hardware" in body


# ------------------------------------------------------------------ agreement (exit check)


def test_gold_sheet_round_trip_and_agreement(tmp_path) -> None:  # type: ignore[no-untyped-def]
    from app.pipeline.repro.agreement import cohen_kappa, compare, load_gold, write_template

    checklist = load_checklist()
    sheet = tmp_path / "gold.csv"
    write_template(sheet, ["p1"], checklist)
    rows = sheet.read_text(encoding="utf-8").splitlines()
    assert len(rows) == 1 + len(checklist.items)
    # Annotate three items, with an alias ("yes") and a blank (skipped) row.
    filled = [rows[0]]
    for row in rows[1:]:
        if row.startswith("p1,code_url,"):
            row = row.replace(",,,", ",yes,1,", 1)
        elif row.startswith("p1,hardware,"):
            row = row.replace(",,,", ",missing,,", 1)
        elif row.startswith("p1,memory,"):
            row = row.replace(",,,", ",n/a,,", 1)
        filled.append(row)
    sheet.write_text("\n".join(filled) + "\n", encoding="utf-8")
    gold = load_gold(sheet)
    assert gold == {("p1", "code_url"): "present", ("p1", "hardware"): "missing",
                    ("p1", "memory"): "not_applicable"}  # fmt: skip

    items = [
        ItemResult(id=i.id, group=i.group, description=i.description, weight=i.weight,
                   status={"code_url": "present", "hardware": "present"}.get(i.id, "unknown"))  # type: ignore[arg-type]
        for i in checklist.items
    ]  # fmt: skip
    card = Scorecard(checklist_version=2, score=None, groups=[], items=items)
    a = compare({"p1": card}, gold)
    assert (a.agreed, a.compared) == (1, 3)  # "unknown" for memory counts as disagreement
    assert ("p1", "hardware", "missing", "present") in a.disagreements
    assert cohen_kappa([("a", "a"), ("b", "b")]) == 1.0
    assert cohen_kappa([("a", "b"), ("b", "a")]) < 0

    bad = tmp_path / "bad.csv"
    bad.write_text("paper_id,item_id,status\np1,code_url,maybe\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unknown status"):
        load_gold(bad)
