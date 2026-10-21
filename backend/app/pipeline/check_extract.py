"""Phase 2 exit check: a full Overview for each arXiv paper in <= 3 minutes, and every item
has an evidence quote that the verifier located (so its chip can highlight it).

    uv run python -m app.pipeline.check_extract                 # default 10 papers
    uv run python -m app.pipeline.check_extract 1706.03762 ...  # your own arXiv ids
    uv run python -m app.pipeline.check_extract --pdf-dir ./pdfs --limit 3

Needs GROBID and GEMINI_API_KEY. Runs parse -> structure -> extract -> verify in-process, with
a fresh in-memory LLM cache so the timing is real (about 6 LLM calls per paper). Writes
report.json and report.md (every paper's Overview, as the Markdown export) to
<data_dir>/phase2_check/.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from collections import Counter
from pathlib import Path
from typing import Any

from app.config import get_settings
from app.llm.cache import MemoryCache
from app.llm.client import build_client
from app.pipeline import export
from app.pipeline.check_parse import DEFAULT_IDS
from app.pipeline.extract.extractor import extract_document
from app.pipeline.ingest.resolver import resolve
from app.pipeline.ingest.sources import SourceFetcher
from app.pipeline.ingest.validate import validate_pdf
from app.pipeline.parse import get_parser
from app.pipeline.parse.grobid import GrobidParser
from app.pipeline.structure.sections import structure_document
from app.pipeline.verify.grounding import ground, grounding_score

TIME_LIMIT_SECONDS = 180
# Fields every ML paper states somewhere; an empty one usually means a missed section.
CORE_FIELDS = ("problem", "contributions", "method_summary", "datasets", "metrics")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("ids", nargs="*", help="arXiv ids (default: the Phase 1 papers)")
    ap.add_argument("--pdf-dir", type=Path, help="use local PDFs instead of downloading")
    ap.add_argument("--limit", type=int, default=0, help="only the first N papers")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    settings = get_settings()
    out_dir = Path(settings.app.data_dir) / "phase2_check"
    pdf_dir = Path(settings.app.data_dir) / "phase1_check" / "pdfs"  # shared with check_parse
    pdf_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    parser = get_parser(settings, "grobid")
    if isinstance(parser, GrobidParser) and not parser.is_alive():
        print(f"GROBID is not reachable at {settings.grobid_url}; run `docker compose up grobid`")
        return 2
    llm = build_client(settings, MemoryCache())
    if not llm.providers:
        print("No LLM provider configured: set GEMINI_API_KEY in the repo-root .env")
        return 2

    if args.pdf_dir:
        papers = [(p.stem, p) for p in sorted(args.pdf_dir.glob("*.pdf"))]
    else:
        papers = [(i, None) for i in (args.ids or DEFAULT_IDS)]
    if args.limit:
        papers = papers[: args.limit]
    fetcher = SourceFetcher(settings)
    results: list[dict[str, Any]] = []
    md: list[str] = ["# Phase 2 extraction check\n"]

    for n, (name, local) in enumerate(papers):
        row: dict[str, Any] = {"id": name}
        try:
            path = local or pdf_dir / f"{name.replace('/', '_')}.pdf"
            if not path.exists():
                if n:
                    time.sleep(3)  # arXiv asks for at most one request every 3 s
                path.write_bytes(fetcher.fetch(resolve(name)).pdf)
            validate_pdf(path.read_bytes(), settings.ingest)
            # Only pipeline time counts towards the limit, not the download.
            started = time.monotonic()
            doc = parser.parse(path)
            roles = structure_document(doc, llm).block_roles
            for block in doc.blocks:
                block.role = roles.get(block.id)
            run = extract_document(
                doc, llm, metadata={}, max_group_chars=settings.extraction.max_group_chars
            )
            verify = ground(run.extraction, doc, llm, path)
            seconds = time.monotonic() - started
            row |= _summarize(run, verify, seconds)
            md += [f"## {name}\n", export.to_markdown(run.extraction), ""]
        except Exception as exc:
            row |= {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            row["trace"] = traceback.format_exc(limit=3)
        results.append(row)
        print(f"{name:<14} {_line(row)}", flush=True)

    passed = [r for r in results if r.get("ok")]
    print(f"\npapers passing: {len(passed)}/{len(results)}")
    (out_dir / "report.json").write_text(
        json.dumps(results, indent=2, default=str, ensure_ascii=False), encoding="utf-8"
    )
    (out_dir / "report.md").write_text("\n".join(md), encoding="utf-8")
    print(f"report: {out_dir / 'report.md'}")
    ok = bool(results) and len(passed) == len(results)
    print("PHASE 2 EXIT CRITERION:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def _summarize(run: Any, verify: Any, seconds: float) -> dict[str, Any]:
    ex = run.extraction
    items = ex.all_items()
    statuses = Counter(e.grounding_status for _, i in items for e in i.evidence)
    no_evidence = [i.id for _, i in items if not i.evidence]
    # A located quote without boxes cannot be highlighted: that breaks the exit criterion.
    no_boxes = [
        i.id
        for _, i in items
        for e in i.evidence
        if e.grounding_status != "unlocated" and not e.boxes
    ]
    failed_groups = [f"{g.name}: {g.error}" for g in run.groups if g.status == "failed"]
    empty_core = [f for f in CORE_FIELDS if not getattr(ex, f)]
    problems = []
    if seconds > TIME_LIMIT_SECONDS:
        problems.append(f"took {seconds:.0f}s > {TIME_LIMIT_SECONDS}s")
    if failed_groups:
        problems.append("failed groups: " + "; ".join(failed_groups))
    if no_evidence:
        problems.append(f"{len(no_evidence)} items without evidence")
    if no_boxes:
        problems.append(f"{len(no_boxes)} located quotes without boxes")
    return {
        "ok": not problems,
        "problems": problems,
        "seconds": round(seconds, 1),
        "items": len(items),
        "per_field": {name: len(getattr(ex, name)) for name, _ in export.SECTIONS},
        "evidence_status": dict(statuses),
        "grounding_score": grounding_score(ex),
        "unlocated": verify.unlocated,
        "llm_calls": run.calls + verify.support_calls,
        "empty_core_fields": empty_core,  # reported, not failed: a paper may lack one
        "warnings": verify.warnings,
    }


def _line(row: dict[str, Any]) -> str:
    if "error" in row:
        return f"ERROR {row['error']}"
    status = row["evidence_status"]
    text = (
        f"{row['seconds']:>5}s {row['items']:>3} items  grounding {row['grounding_score']:.2f}  "
        f"verified {status.get('verified', 0)} partial {status.get('partial', 0)} "
        f"unsupported {status.get('unsupported', 0)} unlocated {status.get('unlocated', 0)}"
    )
    if row["empty_core_fields"]:
        text += f"  empty: {','.join(row['empty_core_fields'])}"
    return text + ("" if row["ok"] else "  FAIL: " + " | ".join(row["problems"]))


if __name__ == "__main__":
    sys.exit(main())
