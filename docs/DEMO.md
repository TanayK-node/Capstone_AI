# PaperLens demo script (about 10 minutes)

One presenter drives the UI; the narration is in quotes. Times are cumulative.

## Before the demo (the day before)

1. `docker compose up --build`; open http://localhost:8000/api/health and check GROBID and
   Gemini are green.
2. Analyse the demo papers **in advance**, one at a time (free-tier quota: about 6 Gemini
   calls each; results are cached, so re-opening them later costs nothing):
   - Attention Is All You Need (`1706.03762`)
   - BERT (`1810.04805`)
   - one math-heavy paper for the Math tab, e.g. DDPM (`2006.11239`)
3. For BERT, press **Write review** on the Review tab once (one more Gemini call), and
   download its Word report once to check it opens.
4. Keep one paper **not** analysed (e.g. ViT, `2010.11929`) for the live upload in step 1.
   If the network or quota fails on the day, skip the live upload and narrate step 1 with
   the Pipeline tab of an already analysed paper.
5. Browser at 125% zoom, window maximised, the library page open.

## 1. Upload (0:00 to 1:30)

Paste `2010.11929` into the link box and press **Analyze**.

> "PaperLens takes a PDF or a link: arXiv, DOI, OpenReview, ACL. The Pipeline tab shows
> every stage as it runs: GROBID parses the PDF into blocks with coordinates, we rebuild the
> results tables from word positions, label the sections, then Gemini extracts the fields
> one section group at a time. Every stage records the model and prompt version it used."

Leave it running; switch to the already analysed BERT paper.

## 2. Grounded overview (1:30 to 3:00)

BERT, **Overview** tab. Click the evidence chip of a hyperparameter (learning rate 1e-4).

> "Every item carries the sentence it came from. Python finds that quote in the PDF and
> highlights it: green when a second check says the sentence supports the item, amber when
> it only partly does, red when it does not, grey when the quote could not be found at
> all. Nothing unverified is hidden; it is marked."

Point at the status colours and the page numbers.

## 3. Reproducibility and claims (3:00 to 5:00)

**Reproducibility** tab.

> "A checklist of the items a replication needs: code, data, hyperparameters, seeds,
> compute. Rules decide what they can (a GitHub link, a seed mention); the LLM judges the
> rest with a quote. The score is a weighted mean computed in Python, never by the LLM."

**Claims** tab.

> "Claims with numbers are checked against the paper's own tables. The LLM only copies the
> claim; Python finds the cells and recomputes the difference. If the table cannot be
> matched without ambiguity we say 'unsupported', never 'contradicted', so a parsing miss
> never makes a paper look wrong."

**Results** tab: show a table, the best value per column in green, the paper's own rows tinted.

## 4. Code (5:00 to 6:00)

**Code** tab.

> "PaperLens finds the paper's own repository from the text, as opposed to libraries it
> merely uses. Where the repository can be cloned, a static scan, nothing is executed,
> compares the hyperparameters with the code. For BERT, the paper pre-trains with learning
> rate 1e-4, batch 256, 1M steps; `run_pretraining.py` defaults to 5e-5, 32 and 100k."

If cloning is not available on the demo machine, show the repository link and say the
comparison runs where cloning is allowed (it was demonstrated on Linux).

## 5. Chat, math, context (6:00 to 8:00)

**Chat**: ask "What learning rate and batch size were used for fine-tuning?"

> "Answers only from the paper's passages, each sentence cites a page; click a citation
> and the PDF jumps there. If nothing relevant is found it refuses without calling the LLM."

Then ask something off-topic ("Who won the 2018 World Cup?") to show the refusal.

DDPM, **Math** tab: the equations rendered with the paper's own macros, then the glossary.

> "The LaTeX source is read from arXiv, never compiled. Each symbol's meaning is grounded
> in a sentence of the paper."

**Context** tab: the citation graph.

> "Key references are the ones cited most in the text, with the citing sentences as
> evidence. Semantic Scholar adds citation counts when it is reachable."

## 6. Reviewer mode and Word report (8:00 to 9:00)

BERT, **Review** tab (written in advance).

> "A draft review: strengths, weaknesses, missing ablations, questions for the authors,
> each point with a quote. Facts from our checks, like the reproducibility gaps, are
> listed separately because Python established them. There is deliberately no score."

Press **Download Word report** and open it: summary first, then every field with page,
evidence status and quote.

## 7. Compare (9:00 to 9:45)

Top bar **Compare**; tick Attention and BERT.

> "Several papers side by side: shared datasets and metrics first, training settings by
> canonical name, and results columns that read the same in both papers. Built from the
> stored results, no LLM. Download as CSV."

## 8. How well it works (9:45 to 10:30)

Show `eval/results/summary.md`.

> "On 10 reference papers: core-field F1 0.72, datasets 0.90, baselines 0.83, numeric
> accuracy of extracted hyperparameters 100%, 80% of items verified against the paper.
> Requiring a found quote cuts the hallucination rate from 10% to 0%. The main gap is
> recall: hyperparameters in appendix tables. The reference annotations were made with an
> LLM and checked by the team, and we say so in the report."

Back to the ViT paper from step 1, which should now be ready.

## Likely questions

- *Why not let the LLM compute the score?* Rule 4: the LLM extracts, Python computes, so
  every number is reproducible and testable.
- *What if the quote is invented?* It is not found in the PDF, so the item is marked
  "quote not found" and counted as unverified (A3 ablation: 10% of items before filtering).
- *Does it run the authors' code?* Never. Static analysis only, in a sandbox container.
- *Cost?* Gemini free tier; about 6 calls per paper, cached per (paper, stage, prompt
  version, model).
