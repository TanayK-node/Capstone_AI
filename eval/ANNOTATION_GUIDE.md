# Annotation guide: extraction gold set

File: `gold/extraction_gold.csv`, one row per gold item:

| column | meaning |
|---|---|
| `paper_id` | arXiv id of the paper |
| `field` | `task`, `datasets`, `baselines`, `metrics`, `hyperparameters`, `compute`, `code_urls` |
| `name` | hyperparameters only: the canonical name (`learning_rate`, `batch_size`, ...; see `backend/app/pipeline/code_check/compare.py` SYNONYMS), else a snake_case name (`beam_size`) |
| `value` | the item as the paper states it (hyperparameters: the value) |
| `aliases` | other ways the paper or common usage writes it, `|`-separated |
| `page` | PDF page where it is stated |
| `note` | scope ("fine-tuning", "ViT-Large", "CIFAR-10 experiments") or remarks |

## Who annotated

The first version (10 papers, the Phase 1-3 reference set) was annotated by an LLM (Claude)
reading each paper's full text, page by page, at the team's request. It was adjudicated once
after the first comparison with PaperLens' output: items the paper states that fit the
definitions below but had been left out were added, never removed to suit the system. Every
change is logged in `gold/CHANGES.md`. The 40 papers added in v2 (50 in all) were annotated
and adjudicated the same way, the adjudication recorded item by item in `gold/audit_v2.csv`.
A spot-check by the team (two or three papers) is recommended before the numbers are cited;
report them as "LLM-annotated, team-checked".

## What counts

- **task**: the problems the paper's experiments address ("machine translation",
  "object detection"). Not the general area ("NLP").
- **datasets**: every dataset used for training or evaluation in the paper's own experiments,
  including pre-training corpora and transfer datasets. A benchmark suite (GLUE, VTAB) is one
  item; its members are aliases. Datasets that are only cited are not included.
- **baselines**: every method the paper reports results against, in tables or text, including
  its own non-proposed baselines ("plain networks"). Ensemble/single variants of one method are
  one item. The paper's own ablated variants are not baselines.
- **metrics**: every evaluation metric reported (BLEU, top-1 error, F1, perplexity). Cost
  measures count when reported as results (inference time, trainable parameters).
- **hyperparameters**: every stated setting of the experiments: optimizer and its parameters,
  learning rates, batch sizes, steps/epochs, warmup, regularisation, model dimensions,
  decoding settings, for every model size and setting the paper states (one row each, scope
  in `note`). Values in tables count. Ranges searched ("lr in {1e-5, 2e-5}") are one row per
  value.
- **compute**: hardware (type and count) and training time, as stated.
- **code_urls**: repositories or pages with the paper's own code or models. Not third-party
  libraries it uses.

Prose fields (problem, contributions, method, novelty, limitations, ...) have no gold list;
they are evaluated only through grounding (is the evidence quote in the paper and does it
support the item).

## Scoring (backend/app/eval/match.py)

- Text fields: an extracted item matches a gold item when the normalised strings are equal or
  nearly so (with the same numbers: CIFAR-10 is not CIFAR-100), or one contains the other and
  the remainder is filler ("BLEU score" / "BLEU"), or the gold phrase inside the extracted text
  is specific on its own (3+ words, a number with a unit, a model-like token such as V100).
  Metrics may carry qualifiers ("validation accuracy" for "accuracy"). An extracted item that
  packs several ("EM and F1", "CIFAR-10/100") is tried part by part.
- Hyperparameters: same name (synonym table or text rule) and the same value after
  normalisation (3e-4 = 0.0003 = "3 x 10^-4"; "6%" = 0.06; "none" = 0).
- Precision: extracted items that match some gold item / extracted items. Recall: gold items
  matched by some extracted item / gold items. F1 per field (micro over papers; macro = mean of
  per-paper F1).
- Hyperparameter coverage: share of (paper, hyperparameter name) pairs in the gold for which a
  correct value was extracted. Numeric accuracy: of the extracted hyperparameters whose name is
  in the gold, the share with a correct value.
- Evidence: share of extracted items whose quote was found and judged supporting
  ("verified"); hallucination rate = items whose quote is not in the paper, not supporting,
  or missing.
