"""Phase 4 exit check: the correct repository is found for >= 80% of papers that have code,
and at least one real paper-code mismatch is shown.

    uv run python -m app.pipeline.check_code --pdf-dir ./pdfs            # full check
    uv run python -m app.pipeline.check_code --pdf-dir ./pdfs --no-llm   # discovery only
    uv run python -m app.pipeline.check_code --pdf-dir ./pdfs --only 1810.04805

Repo discovery needs no LLM (links found by regex). The paper-vs-code comparison needs the
paper's hyperparameters, so it runs parse -> structure -> extract -> verify with Gemini
(about 6 calls per paper), then clones each repository (git, read-only use) and scans it
statically. Expected repositories: eval/gold/code_repos.csv. Writes report.md to
<data_dir>/phase4_check/.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import traceback
from pathlib import Path
from typing import Any

from app.config import REPO_ROOT, get_settings
from app.llm.cache import MemoryCache
from app.llm.client import build_client
from app.pipeline.check_extract import Timer, run_paper
from app.pipeline.check_parse import DEFAULT_IDS
from app.pipeline.code_check.discovery import CONFIRM_BELOW, candidates_from_paper
from app.pipeline.code_check.service import check_code
from app.pipeline.extract.extractor import _add_code_urls
from app.pipeline.ingest.resolver import resolve
from app.pipeline.ingest.sources import SourceFetcher
from app.pipeline.parse import get_parser
from app.pipeline.parse.grobid import GrobidParser
from app.pipeline.results.builder import proposed_names
from app.pipeline.runner import make_github
from app.schemas.code import CodeReport
from app.schemas.extraction import PaperExtraction

GOLD = REPO_ROOT / "eval" / "gold" / "code_repos.csv"
TARGET = 0.8


def load_gold(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return {r["paper_id"].strip(): r["repo_url"].strip() for r in csv.DictReader(f)}


def same_repo(found: str, expected: str) -> bool:
    def key(u: str) -> str:
        return u.lower().rstrip("/").removesuffix(".git").split("/tree/")[0]

    return bool(found) and bool(expected) and key(found).startswith(key(expected))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("ids", nargs="*", help="arXiv ids (default: the Phase 1 papers)")
    ap.add_argument("--pdf-dir", type=Path, help="use local PDFs instead of downloading")
    ap.add_argument("--only", help="only the paper whose id / file name contains this")
    ap.add_argument("--pause", type=float, default=20.0, help="seconds between papers (LLM runs)")
    ap.add_argument("--no-llm", action="store_true", help="repo discovery only, no Gemini")
    ap.add_argument("--gold", type=Path, default=GOLD, help=f"expected repos (default {GOLD})")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    settings = get_settings()
    out_dir = Path(settings.app.data_dir) / "phase4_check"
    pdf_dir = Path(settings.app.data_dir) / "phase1_check" / "pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    gold = load_gold(args.gold)
    parser = get_parser(settings, "grobid")
    if isinstance(parser, GrobidParser) and not parser.is_alive():
        print(f"GROBID is not reachable at {settings.grobid_url}; run `docker compose up grobid`")
        return 2
    llm = None
    if not args.no_llm:
        llm = build_client(settings, MemoryCache())
        if not llm.providers:
            print("No GEMINI_API_KEY: running repo discovery only (--no-llm)")
            llm = None
    github = make_github(settings)

    if args.pdf_dir:
        papers = [(p.stem, p) for p in sorted(args.pdf_dir.glob("*.pdf"))]
    else:
        papers = [(i, None) for i in (args.ids or DEFAULT_IDS)]
    if args.only:
        papers = [p for p in papers if args.only in p[0]]
    fetcher = SourceFetcher(settings)

    rows: list[dict[str, Any]] = []
    md = ["# Phase 4 code check\n"]
    for n, (name, local) in enumerate(papers):
        row: dict[str, Any] = {"id": name, "expected": gold.get(name, "")}
        try:
            path = local or pdf_dir / f"{name.replace('/', '_')}.pdf"
            if not path.exists():
                path.write_bytes(fetcher.fetch(resolve(name)).pdf)
            if llm is not None:
                if n and args.pause:
                    time.sleep(args.pause)
                doc, run, _ = run_paper(path, parser, llm, settings, Timer())
                extraction = run.extraction
            else:
                doc = parser.parse(path)
                extraction = PaperExtraction()
                extraction.metadata.title = doc.metadata.title
                _add_code_urls(extraction, doc)
            names = proposed_names(doc, extraction)
            found = candidates_from_paper(extraction, names)
            top = found[0] if found else None
            row |= {
                "found": top.url if top else "",
                "confidence": top.confidence if top else None,
                "needs_confirmation": bool(top and top.confidence < CONFIRM_BELOW),
            }
            row["repo_ok"] = (
                same_repo(row["found"], row["expected"]) if row["expected"] else not found
            )
            if llm is not None and top is not None:
                # In the app the user confirms an uncertain match; here the expected repo does.
                user = row["expected"] if row["needs_confirmation"] and row["repo_ok"] else None
                report = check_code(
                    extraction,
                    out_dir / "work" / name,
                    method_names=names,
                    github=github,
                    user_repo=user,
                    sandbox=settings.code_check.sandbox,
                    clone_timeout_s=settings.code_check.clone_timeout_s,
                    max_repo_mb=settings.code_check.max_repo_mb,
                    search=False,
                )
                row |= {"code_status": report.status, "counts": report.counts}
                md += _markdown(name, report)
        except Exception as exc:
            row["error"] = f"{type(exc).__name__}: {exc}"
            row["trace"] = traceback.format_exc(limit=3)
        rows.append(row)
        print(_line(row), flush=True)

    with_code = [r for r in rows if r["expected"]]
    ok = [r for r in with_code if r.get("repo_ok")]
    rate = len(ok) / len(with_code) if with_code else 0.0
    mismatches = sum(r.get("counts", {}).get("mismatch", 0) for r in rows)
    print(f"\ncorrect repository: {len(ok)}/{len(with_code)} papers with code = {100 * rate:.0f}%"
          f" (target {100 * TARGET:.0f}%)")  # fmt: skip
    if github is not None:
        github.close()
    (out_dir / "report.json").write_text(json.dumps(rows, indent=2, default=str), encoding="utf-8")
    (out_dir / "report.md").write_text("\n".join(md), encoding="utf-8")
    if llm is None:
        print("paper-code comparison not run (needs GEMINI_API_KEY)")
        print("PHASE 4 EXIT CRITERION: NOT YET (repo part only)")
        return 1
    print(f"paper-code mismatches found: {mismatches}  (details: {out_dir / 'report.md'})")
    passed = rate >= TARGET and mismatches >= 1
    print("PHASE 4 EXIT CRITERION:", "PASS" if passed else "FAIL")
    return 0 if passed else 1


def _line(row: dict[str, Any]) -> str:
    if "error" in row:
        return f"{row['id']:<12} ERROR {row['error']}"
    mark = "OK " if row.get("repo_ok") else "BAD"
    found = row["found"] or "(none)"
    conf = ""
    if row["found"]:
        conf = f" ({row['confidence']:.1f}{', ask user' if row['needs_confirmation'] else ''})"
    text = f"{row['id']:<12} repo {mark} {found}{conf}"
    if "code_status" in row:
        counts = row["counts"]
        text += f"\n{'':12} code: {row['code_status']}  " + "  ".join(
            f"{k} {v}" for k, v in counts.items()
        )
    return text


def _markdown(name: str, report: CodeReport) -> list[str]:
    repo = report.candidates[0].url if report.candidates else "-"
    out = [f"## {name}: {repo}\n", f"status {report.status}, commit {report.commit}, "
           f"sandbox {report.sandbox}, {report.files_scanned} files\n"]  # fmt: skip
    out += ["| status | hyperparameter | paper | code (file:line, kind) |", "|---|---|---|---|"]
    for c in report.comparisons:
        if c.status == "only_in_code":
            continue
        code = "; ".join(f"{p.value} ({p.file}:{p.line or ''}, {p.kind})" for p in c.code_values)
        out.append(f"| {c.status} | {c.paper_name or c.canonical} | {c.paper_value} | {code} |")
    return [*out, ""]


if __name__ == "__main__":
    sys.exit(main())
