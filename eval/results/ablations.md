# Ablations

## A3: evidence policy (post-hoc, same extraction)

Items kept under each policy, scored on the core fields (micro over all papers).

### collect_flash_lite

| policy | items kept | precision | recall | F1 | hallucination rate |
|---|---|---|---|---|---|
| no evidence requirement (keep all) | 2283 | 0.85 | 0.42 | 0.57 | 1% |
| quote found in the paper | 2281 | 0.85 | 0.42 | 0.57 | 1% |
| quote found + verifier: supports or partly | 2255 | 0.85 | 0.42 | 0.56 | 0% |
| quote found + verifier: supports | 2060 | 0.84 | 0.39 | 0.54 | 0% |

### phase2_flash_lite

| policy | items kept | precision | recall | F1 | hallucination rate |
|---|---|---|---|---|---|
| no evidence requirement (keep all) | 421 | 0.97 | 0.54 | 0.69 | 10% |
| quote found in the paper | 386 | 0.97 | 0.47 | 0.63 | 2% |
| quote found + verifier: supports or partly | 379 | 0.97 | 0.46 | 0.62 | 0% |
| quote found + verifier: supports | 337 | 0.96 | 0.43 | 0.59 | 0% |

## A1: parser

| parser | papers | s/paper | sections | paragraphs | tables | tables with grid | references | equations | gold items in parsed text |
|---|---|---|---|---|---|---|---|---|---|
| GROBID (cached TEI) | 10 | cached | 260 | 789 | 74 | 66 | 463 | 67 | 89% |
| PyMuPDF only | 10 | 1.0 | 181 | 3288 | 74 | 74 | 344 | 30 | 93% |

Gold items still findable in the parsed text, by field:

| parser | baselines | compute | datasets | hyperparameters | metrics | task |
|---|---|---|---|---|---|---|
| GROBID (cached TEI) | 99% | 100% | 100% | 77% | 94% | 100% |
| PyMuPDF only | 100% | 100% | 100% | 85% | 100% | 100% |

LaTeX-source and Docling arms: pending (LaTeX needs the arXiv e-prints; Docling is not wired in).

## A6: retrieval for chat

Questions built from the gold set (field questions and one per hyperparameter); recall@5 = gold items whose answer is in the top 5 passages. Parse: GROBID (cached TEI).

| retrieval | items | recall@5 | task | datasets | baselines | metrics | hyperparameters |
|---|---|---|---|---|---|---|---|
| bm25 | 359 | 47% | 58% | 52% | 30% | 37% | 58% |

Dense and hybrid: pending (the embedding model was not available; run with embeddings enabled on a machine that can download it).

## Pending (need Gemini quota; run later)

| ablation | what | needs |
|---|---|---|
| A2 | extraction granularity (whole paper / section groups / per field) | Gemini runs |
| A4 | rule hints (LLM only vs regex hints + LLM) | Gemini runs |
| A5 | model (Gemini Flash vs Flash-Lite) | a check_extract run with Flash |
| A7 | claim verification (LLM verdict vs Python recomputation) | Gemini runs + claim gold |
| A3 full | extraction without asking for quotes | Gemini runs |
| Qasper | grounded QA benchmark, 100 questions | Gemini runs |
