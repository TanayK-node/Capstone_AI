# PaperLens: IEEE conference paper

Two-column IEEE conference paper (`IEEEtran`) on PaperLens.

| file | what |
|---|---|
| `paperlens.tex` | the paper |
| `refs.bib` | references (venues checked against publisher pages, Oct 2026) |
| `figs/` | charts (from `eval/results/`) and screenshots of the app |
| `paperlens.pdf` | compiled version |
| `IEEEtran.cls`, `IEEEtran.bst` | IEEE class and bibliography style, for offline builds |
| `paperlens-latex.zip` | everything above in one file (upload to Overleaf: New project → Upload project) |

Build:

```bash
pdflatex paperlens && bibtex paperlens && pdflatex paperlens && pdflatex paperlens
```

Before submission (search for `TEAM` in `paperlens.tex`): author names and affiliation,
the acknowledgement, and the outcome of the gold-set spot-check (Threats to validity).

Figures: the charts come from `eval/results/` (run `phase2_flash_lite`). The screenshots
show the app with the real Gemini output of that run, loaded from
`eval/runs/phase2_flash_lite/report.md` and re-grounded on the parse.
