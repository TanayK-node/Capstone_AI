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
| `results/` | generated tables (do not edit); `ablations.md` = A3 (every run), A1 and A6 (with `--pdf-dir`; kept from the last such run otherwise) |

## Adding a run (a new model, or an ablation setting)

1. From `backend/`: `uv run python -m app.pipeline.check_extract --pdf-dir <the 10 PDFs>`
   with the setting you want (e.g. another model in `.env`).
2. Copy `data/phase2_check/extractions/` (and `report.md`) to `eval/runs/<name>/`.
3. Run `uv run python -m app.eval.run_eval`; the new run appears as a row next to the others.

`runs/phase2_flash_lite/` is the Phase 2 exit run (Gemini Flash-Lite, Oct 2026).

Ablations without LLM calls: `uv run python -m app.eval.run_eval --pdf-dir <PDFs>`
(add `--tei-dir <cached TEI>` to skip GROBID). Pending, needing Gemini quota: Qasper, A2, A4,
A5, A7, the full A3. A1 and A6 need the PDFs: a later run without `--pdf-dir` keeps the
last A1/A6 sections of `results/ablations.md` instead of erasing them.

## Growing the gold set to 50 papers (`papers.csv`)

`papers.csv` lists the 10 reference papers and 40 new ones (NLP, CV, generative, multimodal,
general ML, graphs, RL, speech, time series; 21 of the 50 from 2022 or later). On a machine that
reaches arXiv, with GROBID running (`docker compose up grobid`), from `backend/`:

```bash
uv run python -m app.eval.collect --no-llm      # 1. PDFs, GROBID TEI, page text (no Gemini)
uv run python -m app.eval.collect               # 2. + PaperLens extraction (~6 Gemini calls/paper)
uv run python -m app.eval.collect --bundle      # 3. pack bundle.zip (+ pdfs.zip)
```

Every step is resumable: stop it at any time (or when the quota runs out: it stops by itself
after 3 papers fail in a row) and run the same command again the next day. A PDF whose first
page does not show the expected title is not processed (wrong id): fix the id and re-run.
`--set new`, `--limit N` and `--only <id or name>` select a batch. Everything goes to
`<data_dir>/eval_collect/`; `status.json` says what is done for each paper.

Upload `bundle.zip` (TEI, page text, the run's extractions and report.md; no PDFs) and, if its
size allows, `pdfs.zip` (needed for the A1/A6 ablations). From the page text the gold rows of
the 40 new papers were annotated the same way as the first 10 (LLM-annotated, gold v2 in
`gold/CHANGES.md`); the run is `runs/collect_flash_lite/` and `run_eval` scores all 50. A1/A6
on all 50 need the PDFs: `run_eval --pdf-dir <data_dir>/eval_collect/pdfs --tei-dir
<data_dir>/eval_collect/tei` on the machine that ran the collector.

## Gemini ablations A2, A3, A5 (`collect --arm` / `--model`)

On the machine that collected the papers (PDFs and TEI in `<data_dir>/eval_collect/`; GROBID
not needed), from `backend/`. Each command is resumable like the collector:

```bash
uv run python -m app.eval.collect --set reference --model gemini-3.5-flash   # A5  -> a5_flash
uv run python -m app.eval.collect --set reference --arm groups     # A2/A3 control -> a2_groups
uv run python -m app.eval.collect --set reference --arm noquote    # A3 no quotes  -> a3_noquote
uv run python -m app.eval.collect --set reference --arm whole      # A2 whole paper -> a2_whole
uv run python -m app.eval.collect --set reference --arm per_field  # A2 per field  -> a2_per_field
uv run python -m app.eval.collect --bundle --run a5_flash,a2_groups,a3_noquote,a2_whole,a2_per_field
```

Gemini calls on the 10 reference papers (extraction + grounding; the section-role step adds
up to one more per paper): A5 about 60 (Flash, ~4 per paper for extraction; grounding stays on
Flash-Lite), groups about 30, noquote 20, whole about 20, per_field about 70. About 200 calls
in all: one day of free-tier quota. The arms (`app/eval/ablate.py`, prompt
`ablation_extract.jinja`) ask only for the scored fields with the production field
definitions; they differ only in what each call sees and whether it must quote. `a2_groups`
is the control both for A2 (granularity) and A3 (quotes). Upload `bundle.zip`; its runs go to
`runs/`, and `run_eval` prints them side by side in `results/ablations.md` ("A2 / A3 / A5").

