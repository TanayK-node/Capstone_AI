---
title: "PaperLens: grounded, reproducibility-aware extraction from research papers"
subtitle: "Capstone project report (draft)"
date: "October 2026"
---

> **Draft.** Sections marked **[TEAM]** need the team's input: names, course details,
> screenshots and the final decisions on pending experiments. Every number below comes
> from a file in the repository, which is named next to it.

# Abstract

Reading a research paper well takes hours, and most of that time goes to finding the same
facts: datasets, baselines, hyperparameters, results, limitations. Whether the paper can be
reproduced is harder still to judge, since papers often leave out seeds, compute and exact
settings, and released code can disagree with the text. LLM summarisers produce fluent text
with no evidence, which is a poor fit for research, where an invented number is worse than
none. PaperLens takes a paper (PDF or link) and returns a structured breakdown in which
every extracted item carries the verbatim sentence it came from. Python locates that
sentence in the PDF and highlights it, and a second check judges whether it supports the
item. On top of this grounded extraction, PaperLens scores reproducibility against a
checklist, checks numeric claims against the paper's own tables, finds the paper's code
repository and compares its settings with the paper, and offers chat that cites pages, a
notation glossary, a citation graph, a draft review, a Word report and a multi-paper
comparison. The LLM (Gemini Flash-Lite, free tier) only extracts. All arithmetic,
matching and verdicts are computed in Python.

On a 50-paper gold set from nine ML areas (2,796 items) the core-field F1 is 0.60
(datasets 0.75, metrics 0.73, baselines 0.66, task 0.51, hyperparameters 0.41), with
precision 0.81 to 0.94 per core field. 91% of extracted hyperparameters whose name matched
the gold had the correct value, 90% of extracted items were verified against the paper and
1% were hallucinated. Of the 246 extracted items of the 40 new papers that match no gold
item, only 10 are wrong when read against the paper; most are correct items the strict
matcher misses, so the scores are lower bounds. On the 10 reference papers the F1 is 0.72,
the same as the first run; in that first run, requiring a located quote lowered the
hallucination rate from 10% to 2%, and adding the support check lowered it to 0%. The gold
set was annotated by an LLM and adjudicated once; we report it as such (section 6.1).

# 1. Introduction

## 1.1 Problem

- **Time.** A careful read takes 1 to 3 hours, mostly spent looking for a fixed set of
  facts.
- **Reproducibility.** Across ML, papers omit seeds, compute, variance and exact
  configurations, and released code often uses different settings from those reported.
- **Trust.** Summarisers give no evidence, so every fact has to be checked against the
  paper by hand.

## 1.2 Goal and users

The pitch is "not just what the paper says, but whether you can reproduce it", with every
extracted fact linked to the exact sentence it came from. Target users are students and
researchers doing literature reviews or planning a reproduction, reviewers who want a
quick checklist pass, and course evaluators who should be able to run the demo live on a
paper they choose.

## 1.3 Contributions

1. An end-to-end system (FastAPI, Celery, PostgreSQL, Next.js) that parses a paper with
   layout coordinates and extracts a fixed schema. Every item carries evidence that is
   located and checked in the PDF.
2. A strict division of labour: **the LLM extracts, Python decides**. Scores, numeric
   comparisons, claim verdicts and paper-vs-code mismatches are computed in Python.
3. A reproducibility scorecard (rules first, one LLM call for the rest), a claim verifier
   that recomputes deltas from parsed tables, and a static paper-vs-code check that never
   runs repository code.
4. An evaluation package (`backend/app/eval/`) with a documented matching scheme, a gold
   set, per-field scores, error lists and three ablations that need no LLM calls (A1
   parser, A3 evidence policy, A6 retrieval).

# 2. Related work **[TEAM]**

Suggested structure, 1 to 2 paragraphs each:

- Scientific information extraction (SciREX; task/dataset/metric extraction).
- Document parsing for science (GROBID, Docling, Nougat/Marker; PDF layout analysis).
- Grounded generation and attribution (quote-then-answer; retrieval-augmented QA such as
  Qasper).
- Reproducibility checklists (NeurIPS paper checklist, ML Reproducibility Challenge) and
  paper-code consistency tools.
- LLM reviewing assistants and their known failure modes.

# 3. Constraints and design principles

Only free resources were available: the Gemini API free tier (roughly 10 to 15 requests per
minute and a few hundred to about 1,500 per day per model, changing without notice) and
laptops. The scope document originally planned a local Qwen model as a fallback; the team
decided against a local model, so the Ollama provider remains in the code but is switched
off (`llm.fallback: null`). The design follows from these limits:

| Rule | What it means in the code |
|---|---|
| Model names only in config | `config/config.yaml`; nothing hard-codes a model ID |
| One LLM gateway | `llm/client.py`: cache, token-bucket rate limiter, retries with backoff, backup model, logging of provider / model / prompt version |
| Schema-validated output | Pydantic schemas; one repair retry, then the stage is marked failed with the error saved |
| LLM never computes | scores, deltas, verdicts and comparisons in Python |
| Evidence on every item | verbatim quote + chunk id; no evidence = "unverified" badge, never silently dropped |
| Versioned prompts | `prompts/*.jinja` with a version string; results keyed by (paper, stage, prompt version, model) |
| Idempotent stages | any stage can be re-run; cached LLM calls cost nothing |
| No code execution | repositories are only parsed (ast / yaml / json / toml), in a sandbox container |
| Small call budget | about 6 Gemini calls per paper for extraction and verification |

# 4. System

## 4.1 Architecture

```
Next.js UI ──HTTP/SSE──> FastAPI ──enqueue──> Celery worker ──> PostgreSQL (+pgvector)
                                                   │
                   GROBID (docker) <───────────────┤
                   Gemini API (llm/client.py) <────┤
                   sandbox container (code scan) <─┘
```

The API stores uploads, enqueues jobs and serves results. All heavy work runs in the worker,
one paper at a time. Progress is streamed to the browser over server-sent events. Without
Redis (for example on Windows), `PAPERLENS_PIPELINE__EAGER=true` runs the pipeline inside
the API process.

**[TEAM]** insert an architecture figure and two or three UI screenshots (Overview with a
highlighted quote; Claims; Compare).

## 4.2 Pipeline

| Stage | Module | LLM? | What it does |
|---|---|---|---|
| ingest | `ingest/` | no | PDF upload, or link resolution (arXiv, DOI, OpenReview, ACL Anthology, PDF URL) |
| parse | `parse/` | no | GROBID TEI and PyMuPDF words → blocks with page coordinates; tables rebuilt from word positions (`tables.reconstruct_table`), located by their caption; references and in-text citations per sentence |
| structure | `structure/` | no | section roles (abstract, method, experiments, appendix, ...), paragraph chunks |
| index | `retrieval/` | no | BM25 (light stemming) + local fastembed vectors for chat |
| extract | `extract/` | yes, one call per section group | schema fields, each with value + verbatim quote + chunk id |
| verify | `verify/` | yes, batched | quote located with rapidfuzz ≥ 90 and mapped to sentence boxes; a support check labels it verified / partial / unsupported; unfound quotes stay, marked "unlocated" |
| repro | `repro/` | one call | checklist (config/checklist.yaml): rules first, the LLM for the rest; score = weighted mean in Python |
| claims | `claims/` | one call | the LLM copies each claim's numbers; Python matches table cells, recomputes deltas and gives the verdict |
| results | `results/` | no | typed results tables: headers, row labels, numbers, best value per column from the header's direction |
| code | `code_check/` | no | repository links ranked from the text; shallow, hardened clone; static scan in the sandbox; paper vs code values via a synonym table |
| math | `math/` | one call | arXiv LaTeX read in memory (never compiled), equations numbered like the PDF, KaTeX with the paper's macros; glossary with grounded symbols |
| context | `context/` | one call | key references = cited most in the text; Semantic Scholar counts and abstracts when reachable; novelty relations, each grounded |
| chat | `chat/` | per question | hybrid retrieval; passages labelled [P1]...; invented markers dropped; uncited answers refused; no relevant passage → refusal with no LLM call |
| review | `review/` | one call (on request) | draft review; findings from repro / claims / code stated by Python; no score |

## 4.3 Grounding

Each LLM item comes with a quote and the id of the chunk it should come from. Python
searches for the quote first in that chunk and then in the whole paper (rapidfuzz partial
ratio ≥ 90), then maps the matched span to sentence boxes so the UI can highlight it.
Table quotes are rows in the form the prompt showed them ("cell | cell") and highlight
that row. A batched support check then labels each located quote: verified, partial or
unsupported. Items whose quote is not found are kept and marked "unlocated", so the user
sees them and the evaluation counts them.

## 4.4 Claims and code: Python gives the verdict

Claims (M8). The LLM only copies a claim's fields and numbers as written. Python finds
candidate cells in the parsed results tables, recomputes the difference or factor, and
compares it within a tolerance set in config. "Contradicted" requires exactly one
unambiguous cell; an ambiguous miss is "unsupported". As a result, a table the parser got
wrong cannot make a paper look wrong.

Code (M7). Repository links are ranked from the text, telling the paper's own code apart
from libraries "based on" which it was built. The clone is shallow, with hooks, symlinks
and local protocols disabled and a size cap. A standalone parse-only scanner reads
argparse defaults, configs and README flags inside the sandbox container. Assignments
under `if not is_training` are skipped. A "match" means the paper's value appears
somewhere in the code; other values found are listed in a note.

## 4.5 User interface

The PDF viewer sits on the left and the analysis tabs on the right, grouped as **Read**
(Overview, Chat, Review), **Check** (Reproducibility, Claims, Results, Code),
**Understand** (Math, Context) and **Debug** (Pipeline, Structure, Block). Clicking an
evidence chip scrolls the PDF to the sentence and highlights it in the colour of its
status. Each paper can be exported as JSON, Markdown, BibTeX, CSV or a Word report. The
Compare page puts 2 to 10 papers side by side.

# 5. Phase results

The project was built in phases with exit criteria (SCOPE.md section 9).

| Phase | Exit criterion | Result |
|---|---|---|
| 1 Ingest and parse | 10 arXiv papers parse; tables on ≥ 8 | passed: `check_parse` 10/10 |
| 2 Grounded extraction | full Overview in ≤ 3 min; every item has a working evidence chip | passed: `check_extract` 10/10, 15 to 50 s per paper |
| 3 Reproducibility | team agreement ≥ 80% on the first 10 papers | accepted below target: 158/210 = 75% agreement, Cohen's κ 0.57 (target 0.6), after per-item guidance (first run 65%) |
| 4 Code and claims | correct repo for ≥ 80% of papers with code; one real mismatch | accepted on discovery: 8/8 repositories found. Mismatch shown for BERT: paper lr 1e-4 / batch 256 / 1M steps vs `run_pretraining.py` defaults 5e-5 / 32 / 100k. Cloning failed on the team's Windows machines and is left as optional |
| 5 Chat, math, context | chat cites pages; glossary for 5 math-heavy papers; graph renders | passed (`check_phase5` on VAE, Adam, DDPM, Transformer, LoRA) |
| 6 Evaluation | metric tables from one command | accepted: `run_eval` produces summary, per-field, per-paper, error and ablation tables; several experiments pending (section 6.5) |
| 7 Polish | stretch features, UI polish, demo script, report | Word report, reviewer mode (F15), comparison matrix (F14), grouped tabs, `docs/DEMO.md`, this report |

Known gaps from Phase 3, should the scorecard be revisited: the training-time item (the
team marked all 10 papers "partial"; the LLM said "present"); "baselines re-run" (the LLM
said "missing" where baselines were compared); README run instructions (only the first 20
KB of a README is read); and long appendices beyond the 48k-character context limit.

# 6. Evaluation

## 6.1 Gold set

`eval/gold/extraction_gold.csv` holds 2,796 items from 50 papers (`eval/papers.csv`):

- **10 reference papers**, used during development (Phases 1-3): Bahdanau et al. 2014, VGG,
  ResNet, Transformer, BERT, RoBERTa, DistilBERT, SimCLR, ViT, LoRA (469 items in v1.1);
- **40 new papers**, added after development and never used to tune the system, spread
  over nine areas: NLP (T5, ELECTRA, SimCSE, RAG, chain-of-thought, ReAct, LLaMA, DPO,
  QLoRA, DeepSeekMath), CV (Faster R-CNN, U-Net, Swin, MAE, ConvNeXt, DINOv2, SAM, ViT
  registers, SigLIP), ML (BatchNorm, AdamW, PGD, Lottery Ticket, scaling laws, Chinchilla,
  FlashAttention, Mamba, KAN), generative models (latent diffusion, DiT, flow matching),
  graphs (GCN, GAT), RL (PPO, SAC), speech (wav2vec 2.0, Whisper), time series (PatchTST,
  iTransformer) and multimodal (LLaVA).

It covers the fields task, datasets, baselines, metrics, hyperparameters, compute and code
URLs. The definitions are in `eval/ANNOTATION_GUIDE.md`. The new papers were downloaded and
run through PaperLens on a team member's laptop with `app.eval.collect` (arXiv is not
reachable from the development container); the bundle it writes holds the page text, the
GROBID TEI and the run.

**How it was made.** For lack of time, the team asked an LLM (Claude) to annotate each paper
from its full text, page by page, following the guide. Each part was adjudicated once after
its first comparison with PaperLens: items that the papers state and that fit the
definitions were added (14 for the reference papers, 34 for the new ones), and one
over-broad alias was removed. No alias was written in the system's wording, and nothing was
removed to suit the system. For the new papers, every extracted item that matched no gold
item was read against the paper and labelled (`eval/gold/audit_v2.csv`, section 6.6).
Every change is logged in `eval/gold/CHANGES.md`. The numbers below therefore measure
agreement with an **LLM-annotated** reference, not with independent human annotation.
**[TEAM]** confirm the spot-check of two or three papers before submission, and record who
checked which.

There is a single annotator and no double annotation, so inter-annotator agreement is not
reported.

## 6.2 Matching and metrics

The scorer is `backend/app/eval/match.py`.

- **Text fields.** Values are normalised first (Unicode NFKD, decimals kept, number words
  turned into digits). Two items match when the strings are equal or nearly so (fuzzy
  ≥ 88 with the same digit sequence, so CIFAR-10 never matches CIFAR-100), or when one
  contains the other and the remainder is filler ("BLEU score" / "BLEU"), or when the gold
  phrase found inside the prediction is specific on its own. Metrics may carry qualifiers
  ("validation accuracy" for "accuracy"). An item that packs several ("EM and F1",
  "CIFAR-10/100") is tried part by part.
- **Hyperparameters.** The name must match (synonym table or text rule) and the values
  must be equal after parsing (3e-4 = 0.0003 = "3 × 10^-4"; "6%" = 0.06; "none" = 0).
- **Reported metrics:**
  - precision, recall and F1 per field (micro over papers; macro = mean of per-paper F1);
  - hyperparameter coverage (share of gold (paper, name) pairs with a correct value
    extracted);
  - numeric accuracy (among extracted hyperparameters whose name is in the gold, the share
    with a correct value);
  - evidence status shares;
  - hallucination rate (items whose quote is not in the paper, does not support the item,
    or is missing).

## 6.3 Main results

Run: `collect_flash_lite` (Gemini Flash-Lite, all 50 papers, pipeline as of Phase 7, run on
the team's laptop). Source: `eval/results/summary.md`.

| Field | Gold | Extracted | Precision | Recall | F1 (micro) | F1 (macro) |
|---|---|---|---|---|---|---|
| task | 172 | 78 | 0.81 | 0.37 | 0.51 | 0.53 |
| datasets | 490 | 320 | 0.94 | 0.63 | 0.75 | 0.79 |
| baselines | 472 | 306 | 0.84 | 0.54 | 0.66 | 0.62 |
| metrics | 239 | 171 | 0.89 | 0.62 | 0.73 | 0.74 |
| hyperparameters | 1310 | 407 | 0.83 | 0.27 | 0.41 | 0.43 |
| compute (not core) | 71 | 70 | 0.54 | 0.51 | 0.52 | 0.59 |
| code_urls | 42 | 68 | 0.44 | 0.69 | 0.54 | 0.73 |

| Headline | Value | Target (SCOPE.md) |
|---|---|---|
| Core-field F1 (micro average) | 0.60 | ≥ 0.80 |
| Hyperparameter coverage | 30% | none |
| Numeric accuracy | 91% | none |
| Verified evidence (automatic proxy for grounding) | 90% | ≥ 90% (human-checked) |
| Hallucination rate | 1% | none |

Evidence status of all 2,283 extracted items: 90% verified, 9% partial, 1% unsupported and
2 items unlocated.

**By paper set and area** (same run):

| Group | Papers | Core-field F1 | HP coverage | Numeric accuracy | Verified |
|---|---|---|---|---|---|
| reference papers | 10 | 0.72 | 40% | 96% | 88% |
| new papers | 40 | 0.57 | 28% | 90% | 91% |
| NLP | 16 | 0.61 | 32% | 93% | 90% |
| CV | 13 | 0.60 | 36% | 91% | 88% |
| ML | 9 | 0.51 | 32% | 89% | 90% |
| generative | 3 | 0.56 | 7% | 80% | 96% |
| graph | 2 | 0.82 | 59% | 100% | 94% |
| RL | 2 | 0.43 | 7% | 80% | 82% |
| speech | 2 | 0.62 | 24% | 89% | 95% |
| time series | 2 | 0.68 | 26% | 100% | 93% |
| multimodal | 1 | 0.79 | 50% | 90% | 94% |

**First run, reference papers only.** `phase2_flash_lite` (prompt versions as of Phase 2):
core-field F1 0.72, hyperparameter coverage 43%, numeric accuracy 100%, verified evidence
80%, hallucination rate 10% (35 of 421 items unlocated). On the same 10 papers the
50-paper run has the same F1 (0.72), coverage 40%, numeric accuracy 96%, 88% verified and
1% hallucinated (2 unlocated). The runs differ in machine, GROBID instance, sampling and
pipeline version; which difference explains the cleaner evidence has not been isolated.

**Reading the numbers.** Precision is high on every core field (0.81 to 0.94), and most of
what precision misses is the matcher, not the extraction (section 6.6). The gap to the 0.80
F1 target comes from recall, mostly on hyperparameters (0.27) and task (0.37). The new
papers score lower than the reference papers, partly because the system was tuned while
reading the reference papers and partly because several new papers state their settings
per model size in appendix tables (LLaMA, Whisper, T5). Areas with two or three papers are
indicative only.

## 6.4 Ablations without LLM calls

Source: `eval/results/ablations.md`.

**A3: evidence policy** (the same extraction, filtered after the fact; core fields):

| Policy | First run (10 papers): kept / P / R / F1 / halluc. | 50-paper run: kept / P / R / F1 / halluc. |
|---|---|---|
| keep everything | 421 / 0.97 / 0.54 / 0.69 / 10% | 2283 / 0.85 / 0.42 / 0.57 / 1% |
| quote found in the paper | 386 / 0.97 / 0.47 / 0.63 / 2% | 2281 / 0.85 / 0.42 / 0.57 / 1% |
| found + supports or partly supports | 379 / 0.97 / 0.46 / 0.62 / 0% | 2255 / 0.85 / 0.42 / 0.56 / 0% |
| found + supports | 337 / 0.96 / 0.43 / 0.59 / 0% | 2060 / 0.84 / 0.39 / 0.54 / 0% |

Requiring evidence removes almost all hallucinated items, but it also costs recall,
because some correct items come with a paraphrased quote that cannot be found. In the
50-paper run nearly every quote is found, so the policies hardly differ. PaperLens keeps
every item and badges it rather than filtering. The user sees the status, and the
hallucination metric still counts the item.

**A1: parser** (all 50 papers, run on the laptop with `--pdf-dir --tei-dir`):

| Parser | Sections | Tables with grid | References | Equations | Gold values found in parsed text |
|---|---|---|---|---|---|
| GROBID (+ PyMuPDF words for tables) | 1,520 | 321 / 436 | 3,026 | 580 | 83% |
| PyMuPDF only | 1,165 | 344 / 344 | 2,394 | 243 | 90% |

By field, GROBID / PyMuPDF: baselines 97% / 99%, compute 92% / 97%, datasets 98% / 100%,
hyperparameters 67% / 81%, metrics 95% / 99%, task 98% / 98%.

GROBID gives the structure the rest of the pipeline relies on: section roles,
references, in-text citations and equations. Raw PyMuPDF text keeps more of the gold
values, mostly numbers in tables, footnotes and appendix lists that GROBID drops. A third
of the gold hyperparameter values never reach the extractor through GROBID's text, so
67% is the ceiling for hyperparameter coverage; the run reaches 30%, less than half of
what the parse makes available.

**A6: chat retrieval** (recall@5 on 2,086 question-item pairs built from the gold set,
GROBID parse):

| Retrieval | All | Task | Datasets | Baselines | Metrics | Hyperparameters |
|---|---|---|---|---|---|---|
| BM25 | 45% | 53% | 36% | 41% | 48% | 50% |
| dense (bge-small) | 36% | 19% | 37% | 29% | 46% | 41% |
| hybrid (RRF) | 45% | 45% | 40% | 38% | 49% | 51% |

Dense retrieval alone is worse, above all on task questions; hybrid ties with BM25 overall
and helps on datasets, metrics and hyperparameters, which supports keeping BM25 in the
chat's fusion.

## 6.5 Pending experiments

These experiments need Gemini quota and were deferred by the team. The runner already lists
them in `eval/results/ablations.md`.

| Experiment | What |
|---|---|
| A2 | extraction granularity: whole paper vs section groups vs per field |
| A4 | rule hints: LLM only vs regex hints + LLM |
| A5 | model: Gemini Flash vs Flash-Lite |
| A7 | claim verdicts: LLM judge vs Python recomputation |
| A3 (full) | extraction without asking for quotes at all |
| A1 LaTeX / Docling | LaTeX-source and Docling parser arms |
| Qasper | grounded QA, 100 questions |
| Dashboard | evaluation dashboard in the UI |

**[TEAM]** run whichever of these quota allows before submission, or keep them in
future work.

## 6.6 Error analysis

Sources: `eval/results/errors_collect_flash_lite.md` (every missed gold item and every
extracted item that matches no gold item, per paper) and `eval/gold/audit_v2.csv`.

The 50-paper run missed 1,602 of 2,796 gold items:

| Field | Missed |
|---|---|
| hyperparameters | 956 |
| baselines | 217 |
| datasets | 182 |
| task | 108 |
| metrics | 91 |
| compute | 35 |
| code URLs | 13 |

**Extracted items that match no gold item.** Each of the 246 such items of the 40 new
papers was read against the paper and labelled:

| Field | Correct, matcher missed | Gold omission (added) | Out of scope | Wrong |
|---|---|---|---|---|
| task | 7 | 1 | 5 | 0 |
| datasets | 7 | 5 | 6 | 4 |
| baselines | 35 | 3 | 6 | 1 |
| metrics | 13 | 1 | 3 | 2 |
| hyperparameters | 54 | 19 | 2 | 2 |
| compute | 11 | 2 | 21 | 0 |
| code URLs | 0 | 0 | 35 | 1 |
| **all** | **127** | **31** | **78** | **10** |

- **Wrong (10):** QLoRA's model families (OPT, LLaMA, BLOOM, Pythia) given as datasets;
  DPO listed as its own baseline; two metrics the paper does not report; two values the
  paper does not state (PPO "epochs = K", a FlashAttention dropout); one code link not in
  the text.
- **Correct, matcher missed (127):** hyperparameter names the synonym table does not join
  ("lambda" vs `loss_weight_lambda` / "λ"; "number of hidden units" vs "hidden units"; a
  Greek ϵ the normaliser drops) and values written in a broken form by the PDF text layer
  ("3.0e^−^4", "8e -4", "2 24" for 2^24).
- **Out of scope (78):** third-party links (libraries, datasets, other papers' code) and
  compute descriptions without hardware or time.

So only 4% of the unmatched items are wrong, and precision is far higher than the table in
6.3 reports. The audit was done by the same LLM annotator (section 7).

The main causes of missed items, with examples:

1. **Appendix and table hyperparameters (largest category).** Large-model papers give
   settings per model size in appendix tables (LLaMA's dimension, heads, layers and
   learning rate for four sizes; Whisper's five sizes; T5's five variants), and the
   extraction usually returns one size. Bahdanau et al.'s embedding size 620, maxout size
   500 and gradient-norm clip 1 (appendix, pp. 14-15) are missed as well. Likely causes:
   the appendix section group is long, and the prompt asks for a quote per item, which
   favours prose over tables.
2. **Task listed too narrowly.** The LLM gives one or two tasks per paper, where the gold
   lists every task the experiments address (VGG's object localisation; SAM's edge
   detection, object proposals and text-to-mask experiments).
3. **Long benchmark lists.** DINOv2 misses 29 of its 42 gold datasets, SAM 20 of 27 and
   Whisper 17 of 21; LLaMA, whose benchmarks are named in running text, misses 4 of 27.
4. **Baselines cited only by author name** (VGG's "Chatfield et al. 2014"; T5's "previous
   best" sources). A matching issue also shows up: "Krizhevsky et al." does not match
   "Krizhevsky et al. 2012", because the scorer requires equal digit sequences.
5. **Parsing ceiling.** 17% of gold values, and 33% of hyperparameter values, are not
   present in the GROBID text at all (A1), so no prompt change can recover them.

**[TEAM]** SCOPE.md asks for at least 100 errors classified by category. The audit above
classifies 246 extracted items; the categories SCOPE.md lists (parsing failure, retrieval
miss, wrong normalisation, hallucinated value, wrong cell match, missing in the paper)
still need to be applied to a sample of the missed items.

# 7. Limitations

- **Gold set:** 50 papers, LLM-annotated by a single annotator, adjudicated once against
  this system's own output (the audit of unmatched items too). Scores may be optimistic
  where the annotator LLM and Gemini share blind spots, and pessimistic where the matcher
  is too strict (the audit shows by how much). Areas outside NLP, CV and ML have one to
  three papers each.
- **Recall:** extraction misses many appendix and table hyperparameters (coverage 30%),
  especially settings given per model size.
- **Reproducibility scorecard:** 75% agreement and κ 0.57, both below target. Agreement
  on items about time and baselines is poor.
- **Code check:** cloning failed on the team's Windows machines, so the paper-vs-code
  comparison was demonstrated only on Linux. Repository discovery works without cloning.
- **External services:** the free-tier quota limits throughput. Semantic Scholar often
  returns HTTP 429, and the context tab then falls back to a PDF-only graph with no
  novelty summary.
- **No offline mode:** the local-model fallback was dropped by team decision.
- **PDFs:** scanned PDFs without a text layer are rejected. LaTeX equations depend on the
  arXiv source being available and readable (Adam's source was not; the PDF equations
  were used instead).
- **Comparison matrix:** results columns are matched across papers by header text alone,
  so the setups may differ. The UI says so.

# 8. Ethics and privacy

Paper text is sent to the Gemini free tier, whose inputs Google may use to improve its
models. The UI warns users not to upload unpublished or confidential papers. Repository
code is never executed. The reviewer mode gives no score, and it labels its output as an
LLM draft, separate from the facts established in Python. It is meant to help a reviewer,
not to replace one.

# 9. Conclusion and future work

PaperLens shows that a free-tier LLM can be made trustworthy for paper analysis by making
it quote its sources and letting deterministic code handle the rest. On 50 papers from
nine areas, extraction precision is high (only 4% of the items the gold set lacks are wrong
when read against the paper), every number is traceable to a sentence, 90% of items are
verified and 1% hallucinated. The main weakness is recall on hyperparameters and tasks.

Future work:

- table-aware hyperparameter extraction from appendices, one row per model size;
- a value normaliser for numbers written with superscripts, and a richer synonym table
  for the scorer;
- the pending ablations (A2, A4, A5, A7) and Qasper;
- human annotation of the gold set, with double annotation on a subset for agreement;
- making cloning work on Windows;
- the remaining Tier 3 features: Repro Kit generator (F12), chart-to-data (F16) and
  audience-level summaries (F17).

# Appendix A: reproducing the results

From `backend/`:

```bash
uv sync
uv run pytest                                   # unit and API tests (SQLite)
uv run python -m app.pipeline.check_parse       # Phase 1 (needs GROBID)
uv run python -m app.pipeline.check_extract     # Phase 2 (needs GROBID + GEMINI_API_KEY)
uv run python -m app.eval.collect               # the 50 papers (needs arXiv + GROBID + Gemini)
uv run python -m app.eval.run_eval --pdf-dir <pdfs> --tei-dir <tei>   # every table + A1/A3/A6
python ../docs/paper/make_figs.py               # the paper's charts
```

The full app: `docker compose up --build` from the repository root. The demo walkthrough is
in `docs/DEMO.md`.

# Appendix B: team and contributions **[TEAM]**

| Member | Contributions |
|---|---|
| | |
