# PaperLens – working rules

See SCOPE.md for the full scope, architecture and phase plan.

## Stack
- Backend: Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2 + Alembic, Celery + Redis, PostgreSQL 16 + pgvector
- Parsing: GROBID (docker), Docling, PyMuPDF; optional Nougat/Marker
- LLM: google-genai SDK (Gemini free tier) behind llm/client.py; model names ONLY from config.
  The Ollama provider still exists but is off (`llm.fallback: null`); the team decided not to use a local model.
- Retrieval: sentence-transformers (local), rank_bm25, optional cross-encoder reranker
- Frontend: Next.js (App Router) + TypeScript + Tailwind + shadcn/ui, react-pdf / PDF.js, TanStack Query
- Tooling: uv or poetry, ruff, mypy, pytest; pnpm, eslint, prettier

## Rules
1. Never hardcode model IDs, API keys or rate limits. Read from config / .env.
2. Every LLM call goes through llm/client.py (cache + rate limit + fallback + logging of provider/model/prompt_version).
3. Every LLM output is validated against a Pydantic schema; one repair retry, then mark the stage failed with the error saved.
4. The LLM never does arithmetic or final verdicts on numbers. Python computes; the LLM extracts.
5. Every extracted item carries evidence (quote + chunk_id). No evidence = unverified badge, never silently dropped.
6. Never execute code from cloned repositories. Static analysis only, inside the sandbox container.
7. Prompts live in prompts/*.jinja with a version string; bump the version on any change.
8. Each pipeline stage is idempotent and re-runnable; results keyed by (paper_id, stage, prompt_version, model).
9. Write unit tests for parsers, normalizers, matchers and verdict logic; use 3 fixture PDFs in tests/fixtures.
10. Prefer targeted changes with inline comments over rewrites of working modules.
11. Build phase by phase as in the scope doc; finish exit criteria before starting the next phase.

## Commands
- Backend (from `backend/`): `uv sync`, `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy app`
- Live provider tests: `uv run pytest -m live` (needs GEMINI_API_KEY in the repo-root .env)
- Provider smoke check: `uv run python -m app.llm.check`
- Migrations: `uv run alembic upgrade head`
- Frontend (from `frontend/`): `pnpm install`, `pnpm dev`, `pnpm lint`, `pnpm build`
- Everything: `docker compose up --build` from the repo root

- Phase 1 exit check: `uv run python -m app.pipeline.check_parse` (needs GROBID; downloads 10 arXiv papers)
- Phase 2 exit check: `uv run python -m app.pipeline.check_extract` (needs GROBID + GEMINI_API_KEY;
  about 6 Gemini calls per paper; `--limit 3` to save quota)
- Phase 3 exit check: `uv run python -m app.pipeline.check_repro --pdf-dir <pdfs>` (needs the team's
  annotations in eval/gold/repro_gold.csv; see eval/gold/README.md)

## Current phase
Phase 4 (code and claims: M7 code check, M8 claim verifier, M9 results tables; Code, Claims,
Results tabs). Exit: correct repo found for >= 80% of papers that have code; at least one real
paper-code mismatch demonstrated.
Phase 3: built, exit check PENDING (the team chose to move on). Run
`check_repro --pdf-dir <pdfs>` with a Gemini key; target >= 80% agreement with
eval/gold/repro_gold.csv. Offline (rules only) it agreed 81% on the 54 items decidable there.
Phase 2 passed: check_extract 10/10 on the reference papers with gemini-3.5-flash-lite,
15-50 s per paper (limit 180 s) (Oct 2026). Phase 1 passed: check_parse 10/10.

## Notes
- Coordinates everywhere are PDF points, origin top-left, pages 1-indexed (schemas/document.py).
- Table grids come from tables.reconstruct_table (PDF word positions), not from GROBID's own grid.
  Tables are located by their own caption ("Table 3:"), since GROBID's table box is often wrong
  or on the wrong page. A grid that fails grid_problem() is dropped: no grid beats a wrong grid.
- When changing table code, re-run it on real papers, not only the synthetic tests:
  `uv run python -m app.pipeline.check_parse --pdf-dir <pdfs>` and read report.md.
- Extraction: one LLM call per section group (extract/groups.py); the LLM returns value + verbatim
  quote + chunk_id. Python normalises values, dedupes, and verify/grounding.py locates each quote
  (rapidfuzz >= 90) and maps it to sentence boxes. Unfound quotes stay, marked "unlocated".
  Table quotes are rows as the prompt shows them ("cell | cell"); they highlight that row.
- Paper status "partial" = parsed fine but extract/verify failed (e.g. no key); re-upload or
  "Re-run analysis" retries only those stages.
- Reproducibility (repro/): checklist in config/checklist.yaml (bump `version` on change). Rules
  decide first (rules.py, plus GitHub API facts: never clone in Phase 3), one LLM call for the rest,
  quotes grounded like extraction; an LLM "present" whose quote is not confirmed is capped at
  "partial". Score = weighted mean in Python; unknown / not_applicable are left out.
  Conventions from the team's gold set (eval/gold/repro_gold.csv, 10 papers): a regex mention
  is a "candidate", not "present" (coverage of the main experiments is judged by the LLM;
  without it, "partial"); with no repository linked, repo items are not_applicable.
- Results tables (results/builder.py, M9): built from the parse, no LLM. A column's own
  header is reliable; a spanning upper label is only a guessed `group` (periodic leaf headers
  split spans; text right under a label means a wrapped header, not a span). Best values use
  the header's direction (error/loss/params: lower is better), else the caption's.
- Tests use SQLite with foreign keys enforced (db.make_engine); the app uses Postgres.
- Docling is not wired in yet (its models download from Hugging Face); it is an A1 ablation option.
