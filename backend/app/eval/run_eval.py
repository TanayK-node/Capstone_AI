"""Phase 6: every metric table from one command.

    uv run python -m app.eval.run_eval                 # every run in eval/runs/
    uv run python -m app.eval.run_eval --runs phase2_flash_lite
    uv run python -m app.eval.run_eval --pdf-dir <the 10 PDFs>   # + parser / retrieval ablations

A run is a directory eval/runs/<name>/ holding PaperLens' output for the gold papers: a
check_extract report.md, or extractions/<paper id>.json. Ablations are runs too (one
directory per setting), so they land in the same tables. Writes eval/results/:
summary.md (headline table, one row per run; breakdown by paper set and research area
from eval/papers.csv; every run on the papers they share), by_field.csv, by_paper.csv,
errors_<run>.md (what each run missed or got wrong, for the error analysis) and
ablations.md (A3 for every run; A1 parser and A6 retrieval when --pdf-dir is given: GROBID
from --tei-dir if given, else the live GROBID server; dense / hybrid retrieval when the local
embedding model is available).
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections.abc import Callable
from pathlib import Path

from app.config import REPO_ROOT, get_settings
from app.eval import ablations
from app.eval.data import SCORED_FIELDS, GoldItem, PredItem, load_gold, load_predictions
from app.eval.extraction import CORE_FIELDS, ExtractionReport, evaluate
from app.schemas.document import ParsedDocument

EVAL_DIR = REPO_ROOT / "eval"
TARGET_F1 = 0.80  # SCOPE.md success criteria: field F1 >= 0.80 for core fields
TARGET_GROUNDING = 0.90


def _pct(x: float | None) -> str:
    return "-" if x is None else f"{100 * x:.0f}%"


def _num(x: float | None) -> str:
    return "-" if x is None else f"{x:.2f}"


def predictions_path(run_dir: Path) -> Path | None:
    if (run_dir / "extractions").is_dir() and any((run_dir / "extractions").glob("*.json")):
        return run_dir / "extractions"
    return run_dir / "report.md" if (run_dir / "report.md").exists() else None


def core_f1(rep: ExtractionReport) -> float | None:
    vals = [f1 for f in CORE_FIELDS if (f1 := rep.total(f).f1) is not None]
    return sum(vals) / len(vals) if vals else None


def grounded(rep: ExtractionReport) -> float | None:
    total = sum(rep.status_counts.values())
    return rep.status_counts["verified"] / total if total else None


def summary_md(results: dict[str, ExtractionReport], gold_papers: int) -> str:
    out = ["# Evaluation summary", "",
           f"Gold set: `eval/gold/extraction_gold.csv` ({gold_papers} papers). Reference "
           "annotations made by an LLM (Claude) from the papers' full text and adjudicated "
           "once against the first run; see `eval/ANNOTATION_GUIDE.md` and "
           "`eval/gold/CHANGES.md`. Spot-check by the team recommended before citing.", "",
           "## Headline", "",
           "| run | papers | core-field F1 (micro avg) | hyperparameter coverage | "
           "numeric accuracy | verified evidence | hallucination rate |",
           "|---|---|---|---|---|---|---|"]  # fmt: skip
    for name, rep in results.items():
        out.append(f"| {name} | {len(rep.papers)} | {_num(core_f1(rep))} | "
                   f"{_pct(rep.hp_coverage)} | {_pct(rep.numeric_accuracy)} | "
                   f"{_pct(grounded(rep))} | {_pct(rep.hallucination_rate)} |")  # fmt: skip
    out += ["", f"Targets (SCOPE.md): core-field F1 >= {TARGET_F1:.2f}; grounding >= "
            f"{100 * TARGET_GROUNDING:.0f}% (the scope's grounding metric is human-checked "
            "support; 'verified evidence' here is the automatic proxy: quote found and judged "
            "supporting).", ""]  # fmt: skip
    for name, rep in results.items():
        out += [f"## {name}: per field", "",
                "| field | gold | extracted | precision | recall | F1 (micro) | F1 (macro) |",
                "|---|---|---|---|---|---|---|"]  # fmt: skip
        for f in SCORED_FIELDS:
            t = rep.total(f)
            core = "" if f in CORE_FIELDS else " (not core)"
            out.append(f"| {f}{core} | {t.gold} | {t.pred} | {_num(t.precision)} | "
                       f"{_num(t.recall)} | {_num(t.f1)} | {_num(rep.macro_f1(f))} |")  # fmt: skip
        out += ["", "Evidence status of every extracted item (all fields):", "",
                "| status | items | share |", "|---|---|---|"]  # fmt: skip
        total = sum(rep.status_counts.values())
        for s, n in rep.status_counts.most_common():
            out.append(f"| {s} | {n} | {_pct(n / total if total else None)} |")
        out.append("")
    return "\n".join(out)


def _headline_row(label: str, rep: ExtractionReport) -> str:
    return (f"| {label} | {len(rep.papers)} | {_num(core_f1(rep))} | {_pct(rep.hp_coverage)} | "
            f"{_pct(rep.numeric_accuracy)} | {_pct(grounded(rep))} | "
            f"{_pct(rep.hallucination_rate)} |")  # fmt: skip


def load_paper_groups(path: Path) -> dict[str, tuple[str, str]]:
    """eval/papers.csv: arxiv id -> (set, area); empty when the list is missing."""
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as f:
        return {r["arxiv_id"]: (r["set"], r["area"]) for r in csv.DictReader(f)}


def breakdown_md(gold: list[GoldItem], preds: dict[str, list[PredItem]],
                 groups: dict[str, tuple[str, str]]) -> str:  # fmt: skip
    """The headline metrics per paper set and research area, and on the papers every run
    covers (a 50-paper run next to a 10-paper run is otherwise not a like-for-like row)."""
    head = ["| group | papers | core-field F1 | hyperparameter coverage | numeric accuracy "
            "| verified evidence | hallucination rate |",
            "|---|---|---|---|---|---|---|"]  # fmt: skip
    out = ["## Breakdown", ""]

    def scored(ids: set[str], items: list[PredItem]) -> ExtractionReport:
        return evaluate([g for g in gold if g.paper_id in ids],
                        [p for p in items if p.paper_id in ids])  # fmt: skip

    for name, items in preds.items():
        covered = {p.paper_id for p in items} & {g.paper_id for g in gold}
        if not groups or len(covered) < 2:
            continue
        out += [f"### {name}: by paper set and area", "", *head]
        for i, key in enumerate(("set", "area")):
            for label in sorted({groups[pid][i] for pid in covered if pid in groups}):
                ids = {pid for pid in covered if groups.get(pid, ("", ""))[i] == label}
                out.append(_headline_row(f"{key}: {label}", scored(ids, items)))
        out.append("")
    shared = set.intersection(*({p.paper_id for p in items} for items in preds.values()))
    shared &= {g.paper_id for g in gold}
    if len(preds) > 1 and shared:
        out += [f"### Every run on the {len(shared)} papers they share", "", *head]
        out += [_headline_row(name, scored(shared, items)) for name, items in preds.items()]
        out.append("")
    return "\n".join(out)


def audit_md(paths: list[Path]) -> str:
    """eval/gold/audit_*.csv: a person's (or the annotator's) reading of each extracted item
    that matched no gold item. Shows how much of the precision gap is the strict matcher."""
    out: list[str] = []
    for path in paths:
        with path.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        cats = sorted({r["category"] for r in rows})
        runs = ", ".join(sorted({r["run"] for r in rows}))
        out += [f"## Not-in-gold audit: `{path.name}` ({runs}, {len(rows)} items)", "",
                "| field | " + " | ".join(cats) + " |", "|---" * (len(cats) + 1) + "|"]  # fmt: skip
        for fld in [*SCORED_FIELDS, "all"]:
            sel = [r for r in rows if fld in ("all", r["field"])]
            out.append(f"| {fld} | " + " | ".join(str(sum(r["category"] == c for r in sel))
                                                   for c in cats) + " |")  # fmt: skip
        out.append("")
    return "\n".join(out)


def errors_md(name: str, rep: ExtractionReport) -> str:
    out = [f"# Errors: {name}", "",
           "Missed = gold items no extracted item matched. Not in gold = extracted items "
           "matching no gold item (with their evidence status), to be classified for the "
           "error analysis (SCOPE.md section 8).", ""]  # fmt: skip
    for p in rep.papers:
        out += [f"## {p.paper_id}", ""]
        for f in SCORED_FIELDS:
            missed, wrong = p.missed.get(f, []), p.wrong.get(f, [])
            if not missed and not wrong:
                continue
            out.append(f"### {f}")
            for g in missed:
                label = f"{g.name} = {g.value}" if g.name else g.value
                note = f" ({g.note})" if g.note else ""
                out.append(f"- missed: {label} [p. {g.page}]{note}")
            for x in wrong:
                label = f"{x.name} = {x.value}" if x.name else x.value
                out.append(f"- not in gold: {label} _[{x.status}]_")
            out.append("")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--runs", nargs="*", help="run names under eval/runs/ (default: all)")
    ap.add_argument("--gold", type=Path, default=EVAL_DIR / "gold" / "extraction_gold.csv")
    ap.add_argument("--out", type=Path, default=EVAL_DIR / "results")
    ap.add_argument("--pdf-dir", type=Path, help="the gold papers' PDFs (<arxiv id>.pdf): A1, A6")
    ap.add_argument("--tei-dir", type=Path, help="cached GROBID TEI (<arxiv id>.tei.xml) for A1/A6")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    gold = load_gold(args.gold)
    runs_dir = EVAL_DIR / "runs"
    names = args.runs or sorted(d.name for d in runs_dir.iterdir() if d.is_dir())
    results: dict[str, ExtractionReport] = {}
    preds: dict[str, list[PredItem]] = {}
    for name in names:
        src = predictions_path(runs_dir / name)
        if src is None:
            print(f"{name}: no report.md or extractions/ found, skipped")
            continue
        preds[name] = load_predictions(src)
        results[name] = evaluate(gold, preds[name])
    if not results:
        print("nothing to evaluate")
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    summary = summary_md(results, len({g.paper_id for g in gold}))
    summary += "\n" + breakdown_md(gold, preds, load_paper_groups(EVAL_DIR / "papers.csv"))
    summary += "\n" + audit_md(sorted(args.gold.parent.glob("audit_*.csv")))
    (args.out / "summary.md").write_text(summary, encoding="utf-8")
    with (args.out / "by_field.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["run", "field", "gold", "extracted", "precision", "recall", "f1", "macro_f1"])
        for name, rep in results.items():
            for fld in SCORED_FIELDS:
                t = rep.total(fld)
                w.writerow([name, fld, t.gold, t.pred, t.precision, t.recall, t.f1,
                            rep.macro_f1(fld)])  # fmt: skip
    with (args.out / "by_paper.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["run", "paper_id", *SCORED_FIELDS])
        for name, rep in results.items():
            for p in rep.papers:
                f1s = [_num(p.fields[x].f1) if x in p.fields else "" for x in SCORED_FIELDS]
                w.writerow([name, p.paper_id, *f1s])
    for name, rep in results.items():
        (args.out / f"errors_{name}.md").write_text(errors_md(name, rep), encoding="utf-8")
        print(f"{name}: core-field F1 {_num(core_f1(rep))}, hyperparameter coverage "
              f"{_pct(rep.hp_coverage)}, numeric accuracy {_pct(rep.numeric_accuracy)}, "
              f"verified evidence {_pct(grounded(rep))}, hallucination "
              f"{_pct(rep.hallucination_rate)}")  # fmt: skip
    md = ablations_md(results, gold, args.pdf_dir, args.tei_dir)
    (args.out / "ablations.md").write_text(md, encoding="utf-8")
    print(f"tables: {args.out}")
    return 0


PENDING = [
    ("A2", "extraction granularity (whole paper / section groups / per field)", "Gemini runs"),
    ("A4", "rule hints (LLM only vs regex hints + LLM)", "Gemini runs"),
    ("A5", "model (Gemini Flash vs Flash-Lite)", "a check_extract run with Flash"),
    ("A7", "claim verification (LLM verdict vs Python recomputation)", "Gemini runs + claim gold"),
    ("A3 full", "extraction without asking for quotes", "Gemini runs"),
    ("Qasper", "grounded QA benchmark, 100 questions", "Gemini runs"),
]


def ablations_md(results: dict[str, ExtractionReport], gold: list[GoldItem],
                 pdf_dir: Path | None, tei_dir: Path | None) -> str:  # fmt: skip
    out = ["# Ablations", "", "## A3: evidence policy (post-hoc, same extraction)", "",
           "Items kept under each policy, scored on the core fields (micro over all papers).",
           ""]  # fmt: skip
    runs_dir = EVAL_DIR / "runs"
    for name in results:
        src = predictions_path(runs_dir / name)
        if src is None:
            continue
        preds = load_predictions(src)
        out += [f"### {name}", "",
                "| policy | items kept | precision | recall | F1 | hallucination rate |",
                "|---|---|---|---|---|---|"]  # fmt: skip
        for policy, rep in ablations.a3(gold, preds).items():
            kept = sum(rep.status_counts.values())
            p, r, f1 = ablations.core_scores(rep)
            out.append(f"| {policy} | {kept} | {_num(p)} | {_num(r)} | {_num(f1)} | "
                       f"{_pct(rep.hallucination_rate)} |")  # fmt: skip
        out.append("")
    if pdf_dir is None:
        out += ["A1 and A6 not run: pass --pdf-dir (and --tei-dir) to run them.", ""]
    else:
        out += a1_a6_md(gold, pdf_dir, tei_dir)
    out += ["## Pending (need Gemini quota; run later)", "", "| ablation | what | needs |",
            "|---|---|---|"]  # fmt: skip
    out += [f"| {a} | {what} | {needs} |" for a, what, needs in PENDING]
    return "\n".join(out) + "\n"


def _log(msg: str) -> None:
    """Progress of the slow ablations, on stderr so the tables on stdout stay clean."""
    print(msg, file=sys.stderr, flush=True)


def a1_a6_md(gold: list[GoldItem], pdf_dir: Path, tei_dir: Path | None) -> list[str]:
    from app.pipeline.parse import get_parser
    from app.pipeline.parse.grobid import GrobidParser, parse_with_tei
    from app.pipeline.retrieval.embedder import get_embedder

    settings = get_settings()
    ids = sorted({g.paper_id for g in gold})
    pdfs = {i: pdf_dir / f"{i}.pdf" for i in ids if (pdf_dir / f"{i}.pdf").exists()}
    out = ["## A1: parser", ""]
    parsers: dict[str, Callable[[Path], ParsedDocument]] = {}
    if tei_dir is not None:
        parsers["GROBID (cached TEI)"] = lambda p: parse_with_tei(
            p, (tei_dir / f"{p.stem}.tei.xml").read_bytes()
        )
    else:
        grobid = get_parser(settings, "grobid")
        if isinstance(grobid, GrobidParser) and grobid.is_alive():
            parsers["GROBID"] = grobid.parse
        else:
            out.append("GROBID not reachable and no --tei-dir: GROBID arm skipped.")
    parsers["PyMuPDF only"] = get_parser(settings, "pymupdf").parse
    parsed: dict[str, dict[str, tuple[ParsedDocument, float]]] = {}
    for name, fn in parsers.items():
        _log(f"A1: parsing {len(pdfs)} PDFs with {name}")
        parsed[name] = ablations.parse_all(fn, pdfs, _log)
    stats = [ablations.parse_stats(name, docs, gold) for name, docs in parsed.items()]
    out += ["| parser | papers | s/paper | sections | paragraphs | tables | tables with grid | "
            "references | equations | gold items in parsed text |",
            "|---|---|---|---|---|---|---|---|---|---|"]  # fmt: skip
    for st in stats:
        secs = "cached" if "cached" in st.parser else f"{st.seconds / max(st.papers, 1):.1f}"
        out.append(f"| {st.parser} | {st.papers} | {secs} | {st.sections} | {st.paragraphs} | "
                   f"{st.tables} | {st.tables_with_grid} | {st.references} | {st.equations} | "
                   f"{_pct(st.gold_in_text / st.gold if st.gold else None)} |")  # fmt: skip
    fields = sorted({f for st in stats for f in st.by_field})
    out += ["", "Gold items still findable in the parsed text, by field:", "",
            "| parser | " + " | ".join(fields) + " |", "|---|" + "---|" * len(fields)]  # fmt: skip
    for st in stats:
        cells = [_pct(st.by_field[f][0] / st.by_field[f][1]) if f in st.by_field else "-"
                 for f in fields]  # fmt: skip
        out.append(f"| {st.parser} | " + " | ".join(cells) + " |")
    out += ["", "LaTeX-source and Docling arms: pending (LaTeX needs the arXiv e-prints; Docling "
            "is not wired in).", ""]  # fmt: skip

    _log("A6: loading the embedding model (the first time it is downloaded)")
    embedder = get_embedder(settings)
    first = next(iter(parsed.values()))
    docs = {pid: doc for pid, (doc, _) in first.items()}
    _log(f"A6: retrieval on {len(docs)} papers ({'BM25, dense, hybrid' if embedder else 'BM25'})")
    scores = ablations.retrieval(docs, gold, embedder, _log)
    out += ["## A6: retrieval for chat", "",
            f"Questions built from the gold set (field questions and one per hyperparameter); "
            f"recall@{ablations.K} = gold items whose answer is in the top {ablations.K} "
            f"passages. Parse: {next(iter(parsed))}.", "",
            "| retrieval | items | recall@5 | " + " | ".join(ablations.QUESTIONS)
            + " | hyperparameters |",
            "|---|---|---|" + "---|" * (len(ablations.QUESTIONS) + 1)]  # fmt: skip
    for s in scores:
        cells = [_pct(s.by_field[f][0] / s.by_field[f][1]) if f in s.by_field else "-"
                 for f in [*ablations.QUESTIONS, "hyperparameters"]]  # fmt: skip
        out.append(f"| {s.mode} | {s.items} | {_pct(s.recall)} | " + " | ".join(cells) + " |")
    if embedder is None:
        out.append("")
        out.append("Dense and hybrid: pending (the embedding model was not available; run with "
                   "embeddings enabled on a machine that can download it).")  # fmt: skip
    out.append("")
    return out


if __name__ == "__main__":
    raise SystemExit(main())
