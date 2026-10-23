# Evaluation (Phase 6)

Every metric table comes from one command, from `backend/`:

```bash
uv run python -m app.eval.run_eval
```

It scores every run in `runs/` against the gold set and writes `results/`:
`summary.md` (headline table, one row per run, then per-field tables), `by_field.csv`,
`by_paper.csv` and `errors_<run>.md` (what each run missed or got wrong).

| path | what |
|---|---|
| `ANNOTATION_GUIDE.md` | what each field includes, who annotated, how matching works |
| `gold/extraction_gold.csv` | extraction gold set: 10 papers, task / datasets / baselines / metrics / hyperparameters / compute / code links |
| `gold/CHANGES.md` | every change to the gold set |
| `gold/repro_gold.csv` | reproducibility checklist gold (team-annotated, Phase 3) |
| `gold/code_repos.csv` | official repository per paper (Phase 4) |
| `runs/<name>/` | one system setting's output: `report.md` from `check_extract`, or `extractions/<paper id>.json` |
| `results/` | generated tables (do not edit) |

## Adding a run (a new model, or an ablation setting)

1. From `backend/`: `uv run python -m app.pipeline.check_extract --pdf-dir <the 10 PDFs>`
   with the setting you want (e.g. another model in `.env`).
2. Copy `data/phase2_check/extractions/` (and `report.md`) to `eval/runs/<name>/`.
3. Run `uv run python -m app.eval.run_eval`; the new run appears as a row next to the others.

`runs/phase2_flash_lite/` is the Phase 2 exit run (Gemini Flash-Lite, Oct 2026).
