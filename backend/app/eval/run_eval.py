"""Phase 6: every metric table from one command.

    uv run python -m app.eval.run_eval                 # every run in eval/runs/
    uv run python -m app.eval.run_eval --runs phase2_flash_lite

A run is a directory eval/runs/<name>/ holding PaperLens' output for the gold papers: a
check_extract report.md, or extractions/<paper id>.json. Ablations are runs too (one
directory per setting), so they land in the same tables. Writes eval/results/:
summary.md (headline table, one row per run), by_field.csv, by_paper.csv and
errors_<run>.md (what each run missed or got wrong, for the error analysis).
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from app.config import REPO_ROOT
from app.eval.data import SCORED_FIELDS, load_gold, load_predictions
from app.eval.extraction import CORE_FIELDS, ExtractionReport, evaluate

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
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    gold = load_gold(args.gold)
    runs_dir = EVAL_DIR / "runs"
    names = args.runs or sorted(d.name for d in runs_dir.iterdir() if d.is_dir())
    results: dict[str, ExtractionReport] = {}
    for name in names:
        src = predictions_path(runs_dir / name)
        if src is None:
            print(f"{name}: no report.md or extractions/ found, skipped")
            continue
        results[name] = evaluate(gold, load_predictions(src))
    if not results:
        print("nothing to evaluate")
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "summary.md").write_text(
        summary_md(results, len({g.paper_id for g in gold})), encoding="utf-8"
    )
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
    print(f"tables: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
