# PaperLens: IEEE conference paper

Two-column IEEE conference paper (`IEEEtran`) on PaperLens.

| file | what |
|---|---|
| `paperlens.tex` | the paper |
| `refs.bib` | references (venues checked against publisher pages, Oct 2026) |
| `figs/` | charts (from `eval/results/`) and screenshots of the app |
| `make_figs.py` | redraws the charts from `eval/results/` |
| `paperlens.pdf` | compiled version |
| `IEEEtran.cls`, `IEEEtran.bst` | IEEE class and bibliography style, for offline builds |
| `paperlens-latex.zip` | everything above in one file (upload to Overleaf: New project → Upload project) |

Build:

```bash
pdflatex paperlens && bibtex paperlens && pdflatex paperlens && pdflatex paperlens
```

Before submission: replace the author block (names, e-mails, affiliation) and, if the
conference is double-blind, anonymise it and the acknowledgment. Format: IEEEtran
conference, 7 pages including references (fits 6 + 2 extra-page limits; 6 pages of body
plus references for most others).

Figures: the charts come from `eval/results/` (50-paper run `collect_flash_lite`, earlier
10-paper run `phase2_flash_lite` for A3; A1 on all 50 PDFs from the laptop) and the hand audit
`eval/gold/audit_v2.csv`; `python docs/paper/make_figs.py` redraws fields, papers, A3,
errors and A1 after `run_eval`. The screenshots show the
app with the real Gemini output of the 10-paper run, loaded from
`eval/runs/phase2_flash_lite/report.md` and re-grounded on the parse.
