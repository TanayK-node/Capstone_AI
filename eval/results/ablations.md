# Ablations

## A3: evidence policy (post-hoc, same extraction)

Items kept under each policy, scored on the core fields (micro over all papers).

### collect_flash_lite

| policy | items kept | precision | recall | F1 | hallucination rate |
|---|---|---|---|---|---|
| no evidence requirement (keep all) | 428 | 0.93 | 0.53 | 0.67 | 1% |
| quote found in the paper | 427 | 0.93 | 0.52 | 0.67 | 0% |
| quote found + verifier: supports or partly | 425 | 0.93 | 0.52 | 0.67 | 0% |
| quote found + verifier: supports | 376 | 0.93 | 0.48 | 0.63 | 0% |

### phase2_flash_lite

| policy | items kept | precision | recall | F1 | hallucination rate |
|---|---|---|---|---|---|
| no evidence requirement (keep all) | 421 | 0.97 | 0.54 | 0.69 | 10% |
| quote found in the paper | 386 | 0.97 | 0.47 | 0.63 | 2% |
| quote found + verifier: supports or partly | 379 | 0.97 | 0.46 | 0.62 | 0% |
| quote found + verifier: supports | 337 | 0.96 | 0.43 | 0.59 | 0% |

A1 and A6 not run: pass --pdf-dir (and --tei-dir) to run them.

## Pending (need Gemini quota; run later)

| ablation | what | needs |
|---|---|---|
| A2 | extraction granularity (whole paper / section groups / per field) | Gemini runs |
| A4 | rule hints (LLM only vs regex hints + LLM) | Gemini runs |
| A5 | model (Gemini Flash vs Flash-Lite) | a check_extract run with Flash |
| A7 | claim verification (LLM verdict vs Python recomputation) | Gemini runs + claim gold |
| A3 full | extraction without asking for quotes | Gemini runs |
| Qasper | grounded QA benchmark, 100 questions | Gemini runs |
