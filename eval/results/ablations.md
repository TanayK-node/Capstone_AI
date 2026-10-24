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
| GROBID (cached TEI) | 50 | cached | 1520 | 5199 | 436 | 321 | 3026 | 580 | 83% |
| PyMuPDF only | 50 | 4.9 | 1165 | 21770 | 344 | 344 | 2394 | 243 | 90% |

Gold items still findable in the parsed text, by field:

| parser | baselines | compute | datasets | hyperparameters | metrics | task |
|---|---|---|---|---|---|---|
| GROBID (cached TEI) | 97% | 92% | 98% | 67% | 95% | 98% |
| PyMuPDF only | 99% | 97% | 100% | 81% | 99% | 98% |

LaTeX-source and Docling arms: pending (LaTeX needs the arXiv e-prints; Docling is not wired in).

## A6: retrieval for chat

Questions built from the gold set (field questions and one per hyperparameter); recall@5 = gold items whose answer is in the top 5 passages. Parse: GROBID (cached TEI).

| retrieval | items | recall@5 | task | datasets | baselines | metrics | hyperparameters |
|---|---|---|---|---|---|---|---|
| bm25 | 2086 | 45% | 53% | 36% | 41% | 48% | 50% |
| dense | 2086 | 36% | 19% | 37% | 29% | 46% | 41% |
| hybrid | 2086 | 45% | 45% | 40% | 38% | 49% | 51% |

## Pending (need Gemini quota; run later)

| ablation | what | needs |
|---|---|---|
| A2 | extraction granularity (whole paper / section groups / per field) | Gemini runs |
| A4 | rule hints (LLM only vs regex hints + LLM) | Gemini runs |
| A5 | model (Gemini Flash vs Flash-Lite) | a check_extract run with Flash |
| A7 | claim verification (LLM verdict vs Python recomputation) | Gemini runs + claim gold |
| A3 full | extraction without asking for quotes | Gemini runs |
| Qasper | grounded QA benchmark, 100 questions | Gemini runs |
