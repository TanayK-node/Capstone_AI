# Evaluation summary

Gold set: `eval/gold/extraction_gold.csv` (50 papers). Reference annotations made by an LLM (Claude) from the papers' full text and adjudicated once against the first run; see `eval/ANNOTATION_GUIDE.md` and `eval/gold/CHANGES.md`. Spot-check by the team recommended before citing.

## Headline

| run | papers | core-field F1 (micro avg) | hyperparameter coverage | numeric accuracy | verified evidence | hallucination rate |
|---|---|---|---|---|---|---|
| collect_flash_lite | 50 | 0.60 | 30% | 91% | 90% | 1% |
| phase2_flash_lite | 10 | 0.72 | 43% | 100% | 80% | 10% |

Targets (SCOPE.md): core-field F1 >= 0.80; grounding >= 90% (the scope's grounding metric is human-checked support; 'verified evidence' here is the automatic proxy: quote found and judged supporting).

## collect_flash_lite: per field

| field | gold | extracted | precision | recall | F1 (micro) | F1 (macro) |
|---|---|---|---|---|---|---|
| task | 172 | 78 | 0.81 | 0.37 | 0.51 | 0.53 |
| datasets | 490 | 320 | 0.94 | 0.63 | 0.75 | 0.79 |
| baselines | 472 | 306 | 0.84 | 0.54 | 0.66 | 0.62 |
| metrics | 239 | 171 | 0.89 | 0.62 | 0.73 | 0.74 |
| hyperparameters | 1310 | 407 | 0.83 | 0.27 | 0.41 | 0.43 |
| compute (not core) | 71 | 70 | 0.54 | 0.51 | 0.52 | 0.59 |
| code_urls | 42 | 68 | 0.44 | 0.69 | 0.54 | 0.73 |

Evidence status of every extracted item (all fields):

| status | items | share |
|---|---|---|
| verified | 2060 | 90% |
| partial | 195 | 9% |
| unsupported | 26 | 1% |
| unlocated | 2 | 0% |

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

## Breakdown

### collect_flash_lite: by paper set and area

| group | papers | core-field F1 | hyperparameter coverage | numeric accuracy | verified evidence | hallucination rate |
|---|---|---|---|---|---|---|
| set: new | 40 | 0.57 | 28% | 90% | 91% | 1% |
| set: reference | 10 | 0.72 | 40% | 96% | 88% | 1% |
| area: CV | 13 | 0.60 | 36% | 91% | 88% | 2% |
| area: Generative | 3 | 0.56 | 7% | 80% | 96% | 1% |
| area: Graph | 2 | 0.82 | 59% | 100% | 94% | 0% |
| area: ML | 9 | 0.51 | 32% | 89% | 90% | 1% |
| area: Multimodal | 1 | 0.79 | 50% | 90% | 94% | 6% |
| area: NLP | 16 | 0.61 | 32% | 93% | 90% | 1% |
| area: RL | 2 | 0.43 | 7% | 80% | 82% | 0% |
| area: Speech | 2 | 0.62 | 24% | 89% | 95% | 0% |
| area: Time series | 2 | 0.68 | 26% | 100% | 93% | 0% |

### phase2_flash_lite: by paper set and area

| group | papers | core-field F1 | hyperparameter coverage | numeric accuracy | verified evidence | hallucination rate |
|---|---|---|---|---|---|---|
| set: reference | 10 | 0.72 | 43% | 100% | 80% | 10% |
| area: CV | 4 | 0.73 | 61% | 100% | 77% | 14% |
| area: NLP | 6 | 0.70 | 32% | 100% | 82% | 7% |

### Every run on the 10 papers they share

| group | papers | core-field F1 | hyperparameter coverage | numeric accuracy | verified evidence | hallucination rate |
|---|---|---|---|---|---|---|
| collect_flash_lite | 10 | 0.72 | 40% | 96% | 88% | 1% |
| phase2_flash_lite | 10 | 0.72 | 43% | 100% | 80% | 10% |

## Not-in-gold audit: `audit_v2.csv` (collect_flash_lite, 246 items)

| field | correct, matcher missed | gold omission (added) | out of scope | wrong |
|---|---|---|---|---|
| task | 7 | 1 | 5 | 0 |
| datasets | 7 | 5 | 6 | 4 |
| baselines | 35 | 3 | 6 | 1 |
| metrics | 13 | 1 | 3 | 2 |
| hyperparameters | 54 | 19 | 2 | 2 |
| compute | 11 | 2 | 21 | 0 |
| code_urls | 0 | 0 | 35 | 1 |
| all | 127 | 31 | 78 | 10 |
