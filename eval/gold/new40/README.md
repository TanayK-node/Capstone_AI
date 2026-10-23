# Gold rows for the 40 new papers (in progress)

One CSV per paper (same columns as `../extraction_gold.csv`, no header), annotated by an LLM
(Claude) from the page-tagged full text of each paper, following `../../ANNOTATION_GUIDE.md`.
They are merged into `../extraction_gold.csv` (and logged in `../CHANGES.md` as v2) once all
40 are done; until then `run_eval` scores only the 10 reference papers.
