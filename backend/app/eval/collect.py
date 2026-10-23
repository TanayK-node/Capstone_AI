"""Collect the evaluation papers (eval/papers.csv) on a machine that reaches arXiv and GROBID.

    uv run python -m app.eval.collect --no-llm               # step 1: PDFs, TEI, page text
    uv run python -m app.eval.collect                        # step 2: + PaperLens extraction
    uv run python -m app.eval.collect --set new --limit 10   # a batch of the new papers
    uv run python -m app.eval.collect --bundle               # step 3: pack the zip to upload

Step 2 costs about 6 Gemini calls per paper. Every step writes one file per paper and is
skipped when that file already exists, so the command can be stopped (Ctrl+C, quota) and run
again later; it stops by itself after 3 papers in a row fail in the LLM (quota exhausted).
A downloaded PDF whose first page does not show the expected title is not processed further.

Output in <data_dir>/eval_collect/:
  pdfs/<id>.pdf          tei/<id>.tei.xml       text/<id>.txt (page-tagged, for annotation)
  runs/<run>/extractions/<id>.json   md/<id>.md   status.json
  bundle.zip (TEI, text, run, status; no PDFs)   pdfs.zip (the PDFs, for A1/A6 and highlighting)
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import traceback
import unicodedata
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pymupdf
from rapidfuzz import fuzz

from app.config import REPO_ROOT

EVAL_DIR = REPO_ROOT / "eval"
TITLE_MIN = 85  # partial-ratio of the expected title against the first page's text
MAX_LLM_FAILURES = 3  # consecutive papers failing in the LLM: assume the quota is spent


@dataclass
class PaperRow:
    arxiv_id: str
    name: str
    title: str
    year: str
    area: str
    set: str  # "reference" (the first 10) or "new"

    @property
    def key(self) -> str:
        return self.arxiv_id.replace("/", "_")


def load_papers(path: Path, which: str = "all") -> list[PaperRow]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = [PaperRow(**{k: (v or "").strip() for k, v in r.items()}) for r in csv.DictReader(f)]
    return [r for r in rows if which == "all" or r.set == which]


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())


def title_score(pdf_path: Path, title: str) -> float:
    """How well the expected title appears on the PDF's first page (0-100)."""
    with pymupdf.open(pdf_path) as pdf:
        first = pdf[0].get_text("text") if pdf.page_count else ""
        meta = (pdf.metadata or {}).get("title") or ""
    want = _norm(title)
    return max(fuzz.partial_ratio(want, _norm(first)), fuzz.ratio(want, _norm(meta)))


def page_text(pdf_path: Path) -> str:
    """The PDF's text with a marker per page, so annotations can cite pages."""
    with pymupdf.open(pdf_path) as pdf:
        return "\n".join(f"\n===== page {i} =====\n{p.get_text('text')}"
                         for i, p in enumerate(pdf, start=1))  # fmt: skip


class Status:
    """status.json: one entry per paper with what was done and the last error."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.data: dict[str, dict[str, Any]] = (
            json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        )

    def set(self, key: str, **fields: Any) -> None:
        self.data.setdefault(key, {}).update(fields)
        self.path.write_text(json.dumps(self.data, indent=1, ensure_ascii=False), encoding="utf-8")


@dataclass
class Steps:
    """What collect() calls for each step; injectable for tests."""

    download: Callable[[str], bytes]
    tei: Callable[[Path], bytes] | None  # None: GROBID unavailable, skip TEI and extraction
    extract: Callable[[Path, bytes], tuple[str, str]] | None  # -> (extraction json, markdown)


def collect(rows: list[PaperRow], out: Path, steps: Steps, run: str, *,
            pause: float = 0.0, log: Callable[[str], None] = print) -> Status:  # fmt: skip
    for sub in ("pdfs", "tei", "text", "md", f"runs/{run}/extractions"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    status = Status(out / "status.json")
    llm_failures = 0
    downloaded = extracted = False
    for row in rows:
        k = row.key
        pdf = out / "pdfs" / f"{k}.pdf"
        try:
            if not pdf.exists():
                if downloaded:
                    time.sleep(3)  # arXiv asks for at most one request every 3 s
                pdf.write_bytes(steps.download(row.arxiv_id))
                downloaded = True
            score = title_score(pdf, row.title)
            status.set(k, name=row.name, title_score=round(score))
            if score < TITLE_MIN:
                status.set(k, error=f"title not found on page 1 (score {score:.0f}): wrong id?")
                log(f"{k:<12} TITLE MISMATCH ({score:.0f}) - check the id in eval/papers.csv")
                continue
            text = out / "text" / f"{k}.txt"
            if not text.exists():
                text.write_text(page_text(pdf), encoding="utf-8")
            tei = out / "tei" / f"{k}.tei.xml"
            if steps.tei is not None and not tei.exists():
                tei.write_bytes(steps.tei(pdf))
            ex = out / "runs" / run / "extractions" / f"{k}.json"
            if steps.extract is not None and tei.exists() and not ex.exists():
                if pause and extracted:
                    time.sleep(pause)  # spread Gemini calls (per-minute limits)
                extracted = True
                try:
                    started = time.monotonic()
                    data, md = steps.extract(pdf, tei.read_bytes())
                except Exception:
                    llm_failures += 1
                    raise
                llm_failures = 0
                ex.write_text(data, encoding="utf-8")
                (out / "md" / f"{k}.md").write_text(md, encoding="utf-8")
                status.set(k, extracted=round(time.monotonic() - started, 1))
            status.set(k, error=None)
            log(f"{k:<12} ok   {row.name}")
        except Exception as exc:
            status.set(k, error=f"{type(exc).__name__}: {exc}")
            log(f"{k:<12} ERROR {type(exc).__name__}: {exc}")
            if llm_failures >= MAX_LLM_FAILURES:
                log(f"{MAX_LLM_FAILURES} papers in a row failed in the LLM: stopping (quota?). "
                    "Run the same command again later; finished papers are kept.")  # fmt: skip
                break
    return status


def write_report(rows: list[PaperRow], out: Path, run: str) -> Path:
    """runs/<run>/report.md in eval/papers.csv order, in check_extract's format."""
    parts = ["# PaperLens extraction (app.eval.collect)\n"]
    for r in rows:
        md = out / "md" / f"{r.key}.md"
        if md.exists():
            parts += [f"## {r.arxiv_id}\n", md.read_text(encoding="utf-8"), ""]
    path = out / "runs" / run / "report.md"
    path.write_text("\n".join(parts), encoding="utf-8")
    return path


def bundle(rows: list[PaperRow], out: Path, run: str) -> tuple[Path, Path]:
    write_report(rows, out, run)
    keys = {r.key for r in rows}
    small, pdfs = out / "bundle.zip", out / "pdfs.zip"
    with zipfile.ZipFile(small, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(out / "status.json", "status.json")
        for sub, ext in (("tei", ".tei.xml"), ("text", ".txt")):
            for f in sorted((out / sub).glob(f"*{ext}")):
                if f.name[: -len(ext)] in keys:
                    z.write(f, f"{sub}/{f.name}")
        for f in sorted((out / "runs" / run).rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(out).as_posix())
    with zipfile.ZipFile(pdfs, "w", zipfile.ZIP_STORED) as z:
        for f in sorted((out / "pdfs").glob("*.pdf")):
            if f.stem in keys:
                z.write(f, f"pdfs/{f.name}")
    return small, pdfs


def _live_steps(no_llm: bool) -> Steps:
    from app.config import get_settings
    from app.llm.cache import MemoryCache
    from app.llm.client import build_client
    from app.pipeline import export
    from app.pipeline.check_extract import Timer, run_paper
    from app.pipeline.ingest.resolver import resolve
    from app.pipeline.ingest.sources import SourceFetcher
    from app.pipeline.ingest.validate import validate_pdf
    from app.pipeline.parse import get_parser
    from app.pipeline.parse.grobid import GrobidParser, parse_with_tei

    settings = get_settings()
    fetcher = SourceFetcher(settings)

    def download(arxiv_id: str) -> bytes:
        data = fetcher.fetch(resolve(arxiv_id)).pdf
        validate_pdf(data, settings.ingest)
        return data

    parser = get_parser(settings, "grobid")
    grobid = parser if isinstance(parser, GrobidParser) and parser.is_alive() else None
    if grobid is None:
        print(f"GROBID is not reachable at {settings.grobid_url}: only PDFs and text are "
              "collected (run `docker compose up grobid` for TEI and extraction).")  # fmt: skip
    tei = (lambda p: grobid.fulltext_tei(p.read_bytes())) if grobid is not None else None

    extract = None
    if grobid is not None and not no_llm:
        version = grobid.version()
        llm = build_client(settings, MemoryCache())
        if not llm.providers:
            print("No LLM provider: set GEMINI_API_KEY in the repo-root .env (or use --no-llm).")
        else:

            class _CachedTei:  # run_paper's parser, reading the TEI saved in step 1
                def __init__(self, tei: bytes) -> None:
                    self.tei = tei

                def parse(self, path: Path) -> Any:
                    return parse_with_tei(path, self.tei, parser_version=version)

            def extract(pdf: Path, tei_bytes: bytes) -> tuple[str, str]:
                _doc, run, _verify = run_paper(pdf, _CachedTei(tei_bytes), llm, settings, Timer())
                failed = [f"{g.name}: {g.error}" for g in run.groups if g.status == "failed"]
                if failed:  # keep nothing partial: the next run retries the paper
                    raise RuntimeError("extraction groups failed: " + "; ".join(failed))
                return run.extraction.model_dump_json(indent=1), export.to_markdown(run.extraction)

    return Steps(download=download, tei=tei, extract=extract)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--papers", type=Path, default=EVAL_DIR / "papers.csv")
    ap.add_argument("--set", choices=["all", "reference", "new"], default="all")
    ap.add_argument("--only", help="only papers whose id or name contains this")
    ap.add_argument("--limit", type=int, default=0, help="only the first N papers (after --set)")
    ap.add_argument("--no-llm", action="store_true", help="PDFs, TEI and text only (no Gemini)")
    ap.add_argument("--run", default="collect_flash_lite", help="run name (eval/runs/<run>)")
    ap.add_argument("--pause", type=float, default=20.0, help="seconds between Gemini papers")
    ap.add_argument("--out", type=Path, help="output dir (default <data_dir>/eval_collect)")
    ap.add_argument("--bundle", action="store_true", help="only pack bundle.zip and pdfs.zip")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    from app.config import get_settings

    out = args.out or Path(get_settings().app.data_dir) / "eval_collect"
    out.mkdir(parents=True, exist_ok=True)
    rows = load_papers(args.papers, args.set)
    if args.only:
        rows = [r for r in rows if args.only.lower() in f"{r.arxiv_id} {r.name}".lower()]
    if args.limit:
        rows = rows[: args.limit]
    if args.bundle:
        small, pdfs = bundle(load_papers(args.papers), out, args.run)
        print(f"upload this: {small} ({small.stat().st_size / 1e6:.1f} MB)")
        print(f"and, if the size allows, the PDFs: {pdfs} ({pdfs.stat().st_size / 1e6:.0f} MB)")
        return 0
    try:
        status = collect(rows, out, _live_steps(args.no_llm), args.run, pause=args.pause)
    except KeyboardInterrupt:
        print("\nstopped; run the same command again to continue")
        return 130
    except Exception:
        traceback.print_exc()
        return 1
    done = [r for r in rows if not status.data.get(r.key, {}).get("error")]
    print(f"\n{len(done)}/{len(rows)} papers without errors; details in {out / 'status.json'}")
    nxt = (
        "the same command without --no-llm"
        if args.no_llm
        else ("`uv run python -m app.eval.collect --bundle` and upload bundle.zip")
    )
    print("next: " + nxt)
    return 0 if len(done) == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
