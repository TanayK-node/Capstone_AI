"""Phase 3 exit check: a reproducibility scorecard for each gold paper, and agreement with the
team's annotations of >= 80% of checklist items.

    uv run python -m app.pipeline.check_repro --template          # write the annotation sheet
    uv run python -m app.pipeline.check_repro --pdf-dir ./pdfs    # score + compare
    uv run python -m app.pipeline.check_repro --pdf-dir ./pdfs --only 1706.03762

The annotation sheet is eval/gold/repro_gold.csv: one row per paper x checklist item; fill
in `status` (present / partial / missing / not_applicable) and `page`, judged from the paper
and its repository WITHOUT looking at PaperLens' answer. Rows left empty are skipped.

Runs parse -> structure -> extract -> verify -> repro in-process (about 8 Gemini calls per
paper; GitHub API for the code items). Writes scorecards.json and report.md (every
scorecard plus every disagreement) to <data_dir>/phase3_check/.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from pathlib import Path

from app.config import REPO_ROOT, get_settings
from app.llm.cache import MemoryCache
from app.llm.client import build_client
from app.pipeline import export
from app.pipeline.check_extract import Timer, run_paper
from app.pipeline.check_parse import DEFAULT_IDS
from app.pipeline.ingest.resolver import resolve
from app.pipeline.ingest.sources import SourceFetcher
from app.pipeline.ingest.validate import validate_pdf
from app.pipeline.parse import get_parser
from app.pipeline.parse.grobid import GrobidParser
from app.pipeline.repro.agreement import Agreement, compare, load_gold, write_template
from app.pipeline.repro.analyzer import analyze
from app.pipeline.repro.checklist import load_checklist
from app.pipeline.runner import make_github
from app.schemas.repro import Scorecard

GOLD = REPO_ROOT / "eval" / "gold" / "repro_gold.csv"
TARGET = 0.8


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("ids", nargs="*", help="arXiv ids (default: the Phase 1 papers)")
    ap.add_argument("--pdf-dir", type=Path, help="use local PDFs instead of downloading")
    ap.add_argument("--only", help="only the paper whose id / file name contains this")
    ap.add_argument("--limit", type=int, default=0, help="only the first N papers")
    ap.add_argument("--pause", type=float, default=30.0, help="seconds between papers")
    ap.add_argument("--gold", type=Path, default=GOLD, help=f"annotations (default {GOLD})")
    ap.add_argument("--template", action="store_true", help="write an empty --gold sheet")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    settings = get_settings()
    checklist = load_checklist()
    if args.template:
        if args.gold.exists():
            print(f"{args.gold} exists; not overwriting it (delete it first)")
            return 2
        ids = args.ids or DEFAULT_IDS
        write_template(args.gold, ids, checklist)
        print(f"wrote {args.gold}: {len(ids)} papers x {len(checklist.items)} items")
        return 0

    out_dir = Path(settings.app.data_dir) / "phase3_check"
    pdf_dir = Path(settings.app.data_dir) / "phase1_check" / "pdfs"
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
    github = make_github(settings)

    if args.pdf_dir:
        papers = [(p.stem, p) for p in sorted(args.pdf_dir.glob("*.pdf"))]
    else:
        papers = [(i, None) for i in (args.ids or DEFAULT_IDS)]
    if args.only:
        papers = [p for p in papers if args.only in p[0]]
    if args.limit:
        papers = papers[: args.limit]

    fetcher = SourceFetcher(settings)
    cards: dict[str, Scorecard] = {}
    errors: dict[str, str] = {}
    md: list[str] = ["# Phase 3 reproducibility check\n"]
    for n, (name, local) in enumerate(papers):
        try:
            path = local or pdf_dir / f"{name.replace('/', '_')}.pdf"
            if not path.exists():
                if n:
                    time.sleep(3)
                path.write_bytes(fetcher.fetch(resolve(name)).pdf)
            validate_pdf(path.read_bytes(), settings.ingest)
            if n and args.pause:
                print(f"  (pausing {args.pause:.0f}s between papers)", flush=True)
                time.sleep(args.pause)
            timer = Timer()
            doc, run, _verify = run_paper(path, parser, llm, settings, timer)
            with timer("repro"):
                repro = analyze(
                    doc,
                    run.extraction,
                    checklist,
                    client=llm,
                    github=github,
                    pdf_path=path,
                    max_chars=settings.repro.max_context_chars,
                )
            card = repro.scorecard
            cards[name] = card
            counts = {s: sum(1 for i in card.items if i.status == s) for s in _STATUS_ORDER}
            print(
                f"{name:<14} score {_fmt(card.score):>5}  "
                + "  ".join(f"{k} {v}" for k, v in counts.items() if v)
                + f"  ({timer.total:.0f}s)",
                flush=True,
            )
            md += [f"## {name}: {run.extraction.metadata.title}\n", export.scorecard_markdown(card)]
        except Exception as exc:
            errors[name] = f"{type(exc).__name__}: {exc}"
            print(f"{name:<14} ERROR {errors[name]}", flush=True)
            traceback.print_exc(limit=2)
    if github is not None:
        github.close()

    (out_dir / "scorecards.json").write_text(
        json.dumps({k: v.model_dump(mode="json") for k, v in cards.items()}, indent=2),
        encoding="utf-8",
    )
    ok = _report_agreement(args.gold, cards, errors, md)
    (out_dir / "report.md").write_text("\n".join(md), encoding="utf-8")
    print(f"report: {out_dir / 'report.md'}")
    return 0 if ok else 1


_STATUS_ORDER = ("present", "partial", "missing", "not_applicable", "unknown")


def _fmt(score: float | None) -> str:
    return "n/a" if score is None else f"{score:.0f}"


def _report_agreement(
    gold_path: Path, cards: dict[str, Scorecard], errors: dict[str, str], md: list[str]
) -> bool:
    all_scored = bool(cards) and not errors
    print(f"\nscorecards: {len(cards)}/{len(cards) + len(errors)}")
    if not gold_path.exists():
        print(f"no annotations at {gold_path}: run with --template, fill it in, run again")
        print("PHASE 3 EXIT CRITERION: NOT YET (no gold annotations)")
        return False
    agreement = compare(cards, load_gold(gold_path))
    unannotated = sorted(set(cards) - agreement.papers_annotated)
    _print_agreement(agreement, unannotated)
    md += _agreement_markdown(agreement)
    rate = agreement.rate
    passed = all_scored and not unannotated and rate is not None and rate >= TARGET
    print("PHASE 3 EXIT CRITERION:", "PASS" if passed else "FAIL")
    return passed


def _print_agreement(a: Agreement, unannotated: list[str]) -> None:
    if not a.compared:
        print("no annotated items match the scored papers (check paper_id / item_id)")
        return
    print(
        f"agreement: {a.agreed}/{a.compared} = {100 * (a.rate or 0):.0f}% "
        f"(target {100 * TARGET:.0f}%)   Cohen's kappa: {a.kappa}"
    )
    for group, (ok, total) in sorted(a.per_group.items()):
        print(f"  {group:<10} {ok}/{total}")
    worst = sorted(a.per_item.items(), key=lambda kv: kv[1][0] / kv[1][1])[:5]
    print("  weakest items: " + ", ".join(f"{k} {ok}/{t}" for k, (ok, t) in worst))
    if unannotated:
        print(f"  papers without annotations: {', '.join(unannotated)}")


def _agreement_markdown(a: Agreement) -> list[str]:
    out = ["# Agreement with annotations\n"]
    if a.rate is not None:
        out.append(f"{a.agreed}/{a.compared} = {100 * a.rate:.0f}%, Cohen's kappa {a.kappa}\n")
    out += ["| item | agreed |", "|---|---|"]
    out += [f"| {k} | {ok}/{t} |" for k, (ok, t) in sorted(a.per_item.items())]
    out += ["", "## Disagreements (paper, item, annotators, PaperLens)", ""]
    out += [f"- {p} · {i}: gold **{g}**, system **{s}**" for p, i, g, s in a.disagreements]
    return out


if __name__ == "__main__":
    sys.exit(main())
