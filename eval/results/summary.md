# Evaluation summary

Gold set: `eval/gold/extraction_gold.csv` (10 papers). Reference annotations made by an LLM (Claude) from the papers' full text and adjudicated once against the first run; see `eval/ANNOTATION_GUIDE.md` and `eval/gold/CHANGES.md`. Spot-check by the team recommended before citing.

## Headline

| run | papers | core-field F1 (micro avg) | hyperparameter coverage | numeric accuracy | verified evidence | hallucination rate |
|---|---|---|---|---|---|---|
| phase2_flash_lite | 10 | 0.72 | 43% | 100% | 80% | 10% |

Targets (SCOPE.md): core-field F1 >= 0.80; grounding >= 90% (the scope's grounding metric is human-checked support; 'verified evidence' here is the automatic proxy: quote found and judged supporting).

## phase2_flash_lite: per field

| field | gold | extracted | precision | recall | F1 (micro) | F1 (macro) |
|---|---|---|---|---|---|---|
| task | 31 | 14 | 0.79 | 0.32 | 0.46 | 0.52 |
| datasets | 64 | 50 | 1.00 | 0.81 | 0.90 | 0.83 |
| baselines | 87 | 70 | 0.99 | 0.72 | 0.83 | 0.83 |
| metrics | 51 | 34 | 1.00 | 0.63 | 0.77 | 0.79 |
| hyperparameters | 203 | 71 | 0.99 | 0.36 | 0.53 | 0.55 |
| compute (not core) | 23 | 17 | 0.94 | 0.70 | 0.80 | 0.80 |
| code_urls | 10 | 11 | 0.82 | 0.90 | 0.86 | 0.92 |

Evidence status of every extracted item (all fields):

| status | items | share |
|---|---|---|
| verified | 337 | 80% |
| partial | 42 | 10% |
| unlocated | 35 | 8% |
| unsupported | 7 | 2% |
