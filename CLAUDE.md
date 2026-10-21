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

## Current phase
Phase 3 (reproducibility: M6 analyzer, checklist YAML, Reproducibility tab).
Exit: scorecard for the first 10 gold papers; team spot-checks agree on >= 80% of items.
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
- Tests use SQLite with foreign keys enforced (db.make_engine); the app uses Postgres.
- Docling is not wired in yet (its models download from Hugging Face); it is an A1 ablation option.
