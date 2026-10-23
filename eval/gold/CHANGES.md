# Changes to the extraction gold set

## v1 (Oct 2026): 455 items, 10 papers

Annotated by an LLM (Claude) from the full text of each paper (see `../ANNOTATION_GUIDE.md`).

## v1.1 (Oct 2026): adjudication after the first comparison (run `phase2_flash_lite`)

Added 14 items the papers state that fit the guide's definitions but had been left out
(each row's note ends with "added in adjudication"):

- 1409.1556: learning rate 1e-3 (S=384 nets, localisation fine-tuning).
- 1512.03385: dropout none ("We do not use dropout"); COCO detection mini-batch 8 (RPN) and
  16 (Fast R-CNN), learning rates 0.001 and 0.0001.
- 1706.03762: constituency parsing beam size 21 and length penalty 0.3.
- 1907.11692: 100K and 300K pre-training steps (Table 4).
- 1910.01108: inference batch size 1; Intel Xeon E5-2690 v3 CPU and iPhone 7 Plus (timing).
- 2010.11929: Polyak averaging factor 0.9999.

Removed one alias that matched unrelated metrics ("score" for 1910.01108's GLUE
macro-score). Nothing was removed to suit the system.

## v2 (Oct 2026): 2796 items, 50 papers

40 papers added (`../papers.csv`, set `new`: 4-5 per area across CV, NLP, ML, generative
models, graphs, RL, speech, multimodal and time series), 2293 items. Annotated the same way as
v1: by an LLM (Claude) from each paper's page-tagged full text (the bundle's PyMuPDF page text,
`app.eval.collect`), reading the method, experiments and appendix pages, following
`../ANNOTATION_GUIDE.md`. Not checked by a person yet.

Conventions applied in v2 (all within the guide):

- Hyperparameter tables in appendices are annotated as distinct values (one row per
  (name, value); the column it came from is in the note), not cell by cell.
- Not annotated: wav2vec 2.0's per-subset decoding weights (Tables 7-8: LM weight and word
  insertion penalty per labelled subset); evaluation-only grids (e.g. DINOv2's linear-probe
  learning-rate grid).
- Model families evaluated by prompting (CoT, ReAct) list the prompted models as baselines
  only when the paper compares them; run counts and seeds are not hyperparameters.
- code_urls: only the paper's own code or project page as stated in the text (SAM:
  segment-anything.com; ReAct: react-lm.github.io). Papers that only promise code (PatchTST)
  or give none (Lottery Ticket, Chinchilla) have no code_urls row.

## v2.1 (Oct 2026): adjudication after the first comparison (run `collect_flash_lite`)

Every extracted item of the 40 new papers that matched no gold item (246) was read against
the paper and labelled in `audit_v2.csv`: correct but missed by the matcher (127), gold
omission (31), out of scope (78: mostly third-party or dataset URLs and compute descriptions
without hardware or time), wrong (10). The 31 omissions became 34 rows (a stated range gives
two), each note ending with "added in adjudication":

- 2001.08361 dropout 0.1; 2003.10555 train steps 1.5M (BERT-Small) and 500k (ablations);
  2112.10752 model size 387M (big inpainting model); 2303.15343 batch size 20k, train steps
  107k, 2.4B examples; 2304.02643 large-scale jitter, 120k iterations; 2305.14314 baseline
  search ranges (learning rate 1e-6 / 5e-5, batch size 8 / 128); 2305.18290 sampling
  temperatures 0.0 / 1.0; 2312.00752 learning rates 2e-3, 4e-3, 4e-5 and 16M-token batches
  (DNA); 2404.19756 PDE settings (10000 interior points, 800 boundary points, alpha 0.01).
- Datasets: 2104.08821 ANLI; 2303.15343 Oxford-IIIT Pet, CIFAR-100; 2304.07193 SUN3d;
  2402.03300 GitHub (training mixture).
- Baselines: 2103.14030 Performer; 2112.10752 image regression; 2212.04356 VP-10K+FT.
- Task 2005.11401 knowledge-intensive NLP tasks; metric 2203.15556 toxicity score; compute
  2302.13971 single V100 GPU (inference).

No alias was added in the system's wording and nothing was removed. The 127 "matcher missed"
items stay counted as errors: the matcher is strict on names ("lambda" vs `loss_weight_lambda`
with alias "λ"; "number of hidden units" vs "hidden units") and on values the extraction wrote
in a broken form ("3.0e^−^4", "8e -4", "2 24" for 2^24). The scores are therefore a lower
bound; `run_eval` prints the audit table next to them.
