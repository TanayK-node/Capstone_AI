"""Upload -> ingest -> parse -> structure -> extract -> verify through the API, on SQLite with
the PyMuPDF parser and a fake LLM (no GROBID, Redis or network needed)."""

import random
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.config import Settings, get_settings
from app.db import make_engine
from app.llm.cache import MemoryCache
from app.llm.client import LLMClient
from app.models import Base
from app.pipeline import dispatch, runner
from tests.conftest import FakeClock
from tests.fake_llm import FakePaperProvider

FIXTURES = Path(__file__).parent / "fixtures"
# Tests flip this to simulate a missing GEMINI_API_KEY.
LLM_STATE: dict[str, Any] = {"enabled": True}


@pytest.fixture
def client(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> Iterator[TestClient]:
    engine = make_engine(f"sqlite:///{tmp_path / 'db.sqlite'}")  # foreign keys enforced
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    test_settings = settings.model_copy(
        update={
            "app": settings.app.model_copy(update={"data_dir": tmp_path / "data"}),
            "parsing": settings.parsing.model_copy(update={"parser": "pymupdf"}),
            "repro": settings.repro.model_copy(update={"github_check": False}),  # no network
            "code_check": settings.code_check.model_copy(update={"sandbox": "process"}),
        }
    )
    # The fixture paper links github.com/example/sparseroute: clone a local repo instead.
    from app.pipeline.code_check import clone as clone_mod
    from tests.code_fixture import make_repo

    local = make_repo(tmp_path)

    def local_clone(candidate, dest, **kw):  # type: ignore[no-untyped-def]
        fixed = candidate.model_copy(update={"url": f"file://{local}", "subdir": None})
        return clone_mod.clone(fixed, dest, **{**kw, "allow_file_protocol": True})

    monkeypatch.setattr("app.pipeline.code_check.service.clone", local_clone)
    # Chat: the fake LLM, and a deterministic embedder instead of downloading the model.
    from tests.conftest import FakeEmbedder

    monkeypatch.setattr("app.llm.get_llm_client", lambda: llm)
    monkeypatch.setattr("app.pipeline.runner.get_embedder", lambda s: FakeEmbedder())
    monkeypatch.setattr("app.api.papers.get_embedder", lambda s: FakeEmbedder())

    clock = FakeClock()
    llm = LLMClient(test_settings, {"gemini": FakePaperProvider()}, MemoryCache(), clock=clock,
                    sleep=clock.sleep, rng=random.Random(0))  # fmt: skip
    LLM_STATE["enabled"] = True

    def run_now(s: Settings, paper_id: str, stages: tuple[str, ...] = runner.STAGES) -> str:
        runner.process_paper(
            paper_id,
            settings=test_settings,
            session_factory=factory,
            llm=llm if LLM_STATE["enabled"] else None,
            stages=stages,
        )
        return "inline"

    monkeypatch.setattr(dispatch, "enqueue", run_now)
    monkeypatch.setattr("app.api.papers.get_sessionmaker", lambda: factory)
    from app.main import create_app

    app = create_app()
    app.dependency_overrides[get_settings] = lambda: test_settings
    with TestClient(app) as c:
        yield c


def upload(client: TestClient, name: str) -> dict:  # type: ignore[type-arg]
    with open(FIXTURES / name, "rb") as f:
        resp = client.post("/api/papers", files={"file": (name, f, "application/pdf")})
    assert resp.status_code == 200, resp.text
    return resp.json()  # type: ignore[no-any-return]


def test_upload_runs_pipeline_and_serves_results(client: TestClient) -> None:
    created = upload(client, "paper_single.pdf")
    assert created["duplicate"] is False
    pid = created["paper_id"]

    detail = client.get(f"/api/papers/{pid}").json()
    assert detail["status"] == "ready", detail["error"]
    assert detail["title"] == "Sparse Routing Improves Low-Resource Translation"
    assert {s: v["status"] for s, v in detail["stages"].items()} == {
        "ingest": "done",
        "parse": "done",
        "structure": "done",
        "index": "done",
        "extract": "done",
        "verify": "done",
        "repro": "done",
        "claims": "done",
        "code": "done",
    }
    assert detail["stages"]["parse"]["provider"] == "pymupdf"
    assert detail["parse"]["block_counts"]["table"] == 1
    roles = {s["title"]: s["role"] for s in detail["parse"]["sections"]}
    assert roles["4 Experiments"] == "experiments"

    blocks = client.get(f"/api/papers/{pid}/blocks").json()
    assert len(blocks["pages"]) == 2
    table = next(b for b in blocks["blocks"] if b["type"] == "table")
    assert table["table"]["n_rows"] == 4 and table["role"] == "experiments"

    pdf = client.get(f"/api/papers/{pid}/pdf")
    assert pdf.headers["content-type"] == "application/pdf"
    assert [p["id"] for p in client.get("/api/papers").json()] == [pid]

    extraction = client.get(f"/api/papers/{pid}/extraction").json()
    assert extraction["verified"] is True and extraction["grounding_score"] > 0.8
    data = extraction["data"]
    items = [i for k, v in data.items() if k not in ("metadata", "results") for i in v]
    assert items and all(i["evidence"] for i in items)
    ev = data["contributions"][0]["evidence"][0]
    assert ev["grounding_status"] == "verified" and ev["boxes"]

    tables = client.get(f"/api/papers/{pid}/tables").json()
    assert len(tables) == 1
    rows = {r["label"]: r for r in tables[0]["rows"]}
    assert rows["SparseRoute (ours)"]["is_proposed"] and not rows["Switch"]["is_proposed"]
    best = [c["text"] for r in tables[0]["rows"] for c in r["cells"] if c["is_best"]]
    assert "26.4 ± 0.2" in best and "70" in best  # highest BLEU, lowest FLOPs
    csv_tables = client.get(f"/api/papers/{pid}/tables?format=csv").text
    assert "SparseRoute (ours),26.4 ± 0.2" in csv_tables
    assert any(r["is_proposed"] for r in data["results"])

    report = client.get(f"/api/papers/{pid}/claims").json()["report"]
    claim = next(c for c in report["claims"] if c["kind"] == "improvement")
    assert claim["verdict"] == "supported", claim["explanation"]
    assert claim["recomputed_delta"] == 2.1  # 26.4 - 24.3, computed in Python
    assert {c["row_label"] for c in claim["checked_cells"]} == {"SparseRoute (ours)", "Transformer"}

    code = client.get(f"/api/papers/{pid}/code").json()["report"]
    assert code["status"] == "ok" and code["sandbox"] == "process"
    rows = {r["canonical"]: r for r in code["comparisons"]}
    assert rows["learning_rate"]["status"] == "match"  # README command uses 3e-4
    assert "0.001" in rows["learning_rate"]["note"] or "1e-3" in rows["learning_rate"]["note"]
    assert rows["dropout"]["status"] == "only_in_code"
    assert not Path("/tmp/PAPERLENS_EXECUTED").exists()  # the repo's code never ran

    repro = client.get(f"/api/papers/{pid}/reproducibility").json()
    assert repro["checklist_version"] >= 3 and 0 < repro["score"] < 100
    items = {i["id"]: i for i in repro["scorecard"]["items"]}
    assert items["hardware"]["status"] == "partial" and items["hardware"]["evidence"]


def test_exports(client: TestClient) -> None:
    pid = upload(client, "paper_single.pdf")["paper_id"]
    as_json = client.get(f"/api/papers/{pid}/export?format=json")
    assert as_json.json()["metadata"]["title"].startswith("Sparse Routing")
    md = client.get(f"/api/papers/{pid}/export?format=md").text
    assert md.startswith("# Sparse Routing") and "## Contributions" in md and "p. " in md
    bib = client.get(f"/api/papers/{pid}/export?format=bib").text
    assert bib.startswith("@article{") and "Sparse Routing" in bib
    csv_text = client.get(f"/api/papers/{pid}/export?format=csv").text
    assert csv_text.splitlines()[0].startswith("field,id,value")
    assert "attachment" in as_json.headers["content-disposition"]
    assert client.get(f"/api/papers/{pid}/export?format=xml").status_code == 422


def test_events_stream_ends_with_final_status(client: TestClient) -> None:
    pid = upload(client, "paper_single.pdf")["paper_id"]
    with client.stream("GET", f"/api/papers/{pid}/events") as resp:
        assert resp.headers["content-type"].startswith("text/event-stream")
        body = "".join(resp.iter_text())
    assert "event: stage" in body and '"stage": "verify"' in body
    last = body.strip().split("\n\n")[-1]
    assert last.startswith("event: done") and '"status": "ready"' in last


def test_without_llm_the_paper_is_partial(client: TestClient) -> None:
    LLM_STATE["enabled"] = False
    pid = upload(client, "paper_single.pdf")["paper_id"]
    detail = client.get(f"/api/papers/{pid}").json()
    assert detail["status"] == "partial"
    assert "GEMINI_API_KEY" in detail["error"]
    stages = {s: v["status"] for s, v in detail["stages"].items()}
    assert stages == {
        "ingest": "done",
        "parse": "done",
        "structure": "done",
        "index": "done",  # keyword index needs no LLM
        "extract": "failed",
    }
    assert client.get(f"/api/papers/{pid}/extraction").status_code == 404

    # Re-uploading once a key is set retries only the analysis stages.
    LLM_STATE["enabled"] = True
    again = upload(client, "paper_single.pdf")
    assert again["duplicate"] is True and again["dispatched_to"] == "inline"
    assert client.get(f"/api/papers/{pid}").json()["status"] == "ready"


def test_duplicate_upload_is_not_reprocessed(client: TestClient) -> None:
    first = upload(client, "paper_twocol.pdf")
    second = upload(client, "paper_twocol.pdf")
    assert second == {**first, "duplicate": True, "status": "ready", "dispatched_to": None}


def test_rerun_structure_only_is_idempotent(client: TestClient) -> None:
    pid = upload(client, "paper_single.pdf")["paper_id"]
    before = client.get(f"/api/papers/{pid}/blocks").json()
    resp = client.post(f"/api/papers/{pid}/rerun", json={"stages": ["structure"]})
    assert resp.status_code == 200
    after = client.get(f"/api/papers/{pid}/blocks").json()
    assert before == after
    assert client.get(f"/api/papers/{pid}").json()["status"] == "ready"


@pytest.mark.parametrize(
    ("kwargs", "status", "match"),
    [
        ({"data": {"url": "not a link"}}, 422, "not a recognised"),
        ({}, 422, "exactly one"),
    ],
)
def test_bad_requests(client: TestClient, kwargs: dict, status: int, match: str) -> None:  # type: ignore[type-arg]
    resp = client.post("/api/papers", **kwargs)
    assert resp.status_code == status
    assert match in resp.json()["detail"]


def test_scanned_pdf_rejected(client: TestClient) -> None:
    with open(FIXTURES / "scanned.pdf", "rb") as f:
        resp = client.post("/api/papers", files={"file": ("s.pdf", f, "application/pdf")})
    assert resp.status_code == 422
    assert "text layer" in resp.json()["detail"]


def test_unknown_paper_404(client: TestClient) -> None:
    assert client.get("/api/papers/" + "0" * 64).status_code == 404


def test_chat_answers_with_citations_or_refuses(client: TestClient) -> None:
    pid = upload(client, "paper_single.pdf")["paper_id"]
    detail = client.get(f"/api/papers/{pid}").json()
    assert detail["stages"]["index"]["detail"]["mode"] == "hybrid"

    resp = client.post(
        f"/api/papers/{pid}/chat",
        json={"question": "What learning rate and optimizer do they use?"},
    ).json()
    assert resp["answered"] and resp["retrieval"] == "hybrid"
    assert "Adam" in resp["answer"] and "[P99]" not in resp["answer"]  # invented marker dropped
    cite = resp["citations"][0]
    assert cite["marker"] == "P1" and cite["page"] >= 1 and cite["boxes"]

    off_topic = client.post(
        f"/api/papers/{pid}/chat", json={"question": "Who won the football world cup?"}
    ).json()
    assert off_topic["answered"] is False and off_topic["retrieved"] == []
