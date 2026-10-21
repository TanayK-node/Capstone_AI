"""Upload -> ingest -> parse -> structure through the API, on SQLite with the PyMuPDF parser
(no GROBID, Redis or LLM needed)."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import Settings, get_settings
from app.models import Base
from app.pipeline import dispatch, runner

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def client(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> Iterator[TestClient]:
    engine = create_engine(
        f"sqlite:///{tmp_path / 'db.sqlite'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    test_settings = settings.model_copy(
        update={
            "app": settings.app.model_copy(update={"data_dir": tmp_path / "data"}),
            "parsing": settings.parsing.model_copy(update={"parser": "pymupdf"}),
        }
    )

    def run_now(s: Settings, paper_id: str, stages: tuple[str, ...] = runner.STAGES) -> str:
        runner.process_paper(
            paper_id, settings=test_settings, session_factory=factory, llm=None, stages=stages
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
