import json
import zipfile
from pathlib import Path

from app.eval.collect import (
    EVAL_DIR,
    PaperRow,
    Steps,
    bundle,
    collect,
    load_papers,
    page_text,
    title_score,
)

FIXTURES = Path(__file__).parent / "fixtures"
PDF = (FIXTURES / "paper_single.pdf").read_bytes()
TITLE = "Sparse Routing Improves Low-Resource Translation"


def row(arxiv_id: str = "2401.00001", title: str = TITLE) -> PaperRow:
    return PaperRow(arxiv_id=arxiv_id, name="fixture", title=title, year="2024", area="NLP",
                    set="new")  # fmt: skip


def test_paper_list_is_balanced_and_unique() -> None:
    rows = load_papers(EVAL_DIR / "papers.csv")
    assert len(rows) == 50 and len({r.arxiv_id for r in rows}) == 50
    assert sum(r.set == "reference" for r in rows) == 10
    assert len(load_papers(EVAL_DIR / "papers.csv", "new")) == 40


def test_title_check_and_page_text() -> None:
    pdf = FIXTURES / "paper_single.pdf"
    assert title_score(pdf, TITLE) >= 85
    assert title_score(pdf, "Deep Residual Learning for Image Recognition") < 85
    text = page_text(pdf)
    assert "===== page 1 =====" in text and "===== page 2 =====" in text


def test_collect_is_resumable_and_skips_wrong_titles(tmp_path: Path) -> None:
    calls = {"download": 0, "tei": 0, "extract": 0}

    def download(_id: str) -> bytes:
        calls["download"] += 1
        return PDF

    def tei(_p: Path) -> bytes:
        calls["tei"] += 1
        return (FIXTURES / "paper_single.tei.xml").read_bytes()

    def extract(_p: Path, _t: bytes) -> tuple[str, str]:
        calls["extract"] += 1
        return '{"metadata": {}}', "## Task\n\n- translation _[verified]_\n"

    steps = Steps(download, tei, extract)
    rows = [row(), row("2401.00002", "Attention Is All You Need")]
    status = collect(rows, tmp_path, steps, "r", log=lambda _m: None)
    assert status.data["2401.00001"]["error"] is None
    assert "title not found" in status.data["2401.00002"]["error"]
    assert calls == {"download": 2, "tei": 1, "extract": 1}  # nothing after a wrong title

    collect(rows, tmp_path, steps, "r", log=lambda _m: None)  # re-run: all cached
    assert calls == {"download": 2, "tei": 1, "extract": 1}

    small, pdfs = bundle(rows, tmp_path, "r")
    names = zipfile.ZipFile(small).namelist()
    assert "runs/r/extractions/2401.00001.json" in names and "text/2401.00001.txt" in names
    assert "runs/r/report.md" in names and not any(n.endswith(".pdf") for n in names)
    assert "## 2401.00001" in (tmp_path / "runs/r/report.md").read_text()
    assert zipfile.ZipFile(pdfs).namelist() == ["pdfs/2401.00001.pdf", "pdfs/2401.00002.pdf"]
    assert json.loads((tmp_path / "status.json").read_text())["2401.00001"]["title_score"] >= 85


def test_llm_failures_stop_the_run(tmp_path: Path) -> None:
    def extract(_p: Path, _t: bytes) -> tuple[str, str]:
        raise RuntimeError("429 quota")

    steps = Steps(lambda _i: PDF, lambda _p: b"<TEI/>", extract)
    rows = [row(f"2401.0000{i}") for i in range(1, 6)]
    status = collect(rows, tmp_path, steps, "r", log=lambda _m: None)
    assert len(status.data) == 3  # stopped after 3 consecutive LLM failures
    assert all("429" in v["error"] for v in status.data.values())
