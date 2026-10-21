# Gold annotations

## `repro_gold.csv`: reproducibility checklist (Phase 3 exit, SCOPE.md §8)

One row per paper x checklist item (10 papers x 21 items). Fill in two columns:

| column | what to write |
| --- | --- |
| `status` | `present`, `partial`, `missing` or `not_applicable` (`yes` / `no` / `n/a` also work) |
| `page` | the page where you found it (empty for `missing`) |
| `note` | optional: anything ambiguous |

How to annotate:

- **Do not open PaperLens' scorecard for a paper before annotating it.** The point is to
  check the system against an independent reading.
- Judge from the paper (main text, tables, appendix) and, for the six Code items, from the
  repository linked in the paper (open it on GitHub: license, dependency files, README).
- `present`: clearly stated. `partial`: some of it (e.g. hyperparameters only for the
  proposed method, not the baselines). `missing`: not stated anywhere.
  `not_applicable`: the item cannot apply (e.g. no baselines are compared).
- Each item's full description is in the `description` column and in
  `config/checklist.yaml`. About 15 minutes per paper.
- Split the papers between people; for the spot-check, have a second person re-annotate
  2-3 papers and note where you disagreed with each other.

Then, from `backend/`:

```bash
uv run python -m app.pipeline.check_repro --pdf-dir <the 10 PDFs>
```

It scores every paper, compares with this file, and prints the agreement (target >= 80%),
Cohen's kappa (target >= 0.6), the weakest items, and `PHASE 3 EXIT CRITERION: PASS/FAIL`.
Every disagreement is listed in `data/phase3_check/report.md`.
