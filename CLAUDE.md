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

## Current phase
Phase 1 (ingest, parse, structure). Do not start Phase 2 until `check_parse` reports PASS
(10 arXiv papers parse without errors, tables on >= 8) on a machine that can reach arXiv.

## Notes
- Coordinates everywhere are PDF points, origin top-left, pages 1-indexed (schemas/document.py).
- Table grids come from tables.reconstruct_table (PDF word positions), not from GROBID's own grid.
  Tables are located by their own caption ("Table 3:"), since GROBID's table box is often wrong
  or on the wrong page. A grid that fails grid_problem() is dropped: no grid beats a wrong grid.
- When changing table code, re-run it on real papers, not only the synthetic tests:
  `uv run python -m app.pipeline.check_parse --pdf-dir <pdfs>` and read report.md.
- Tests use SQLite with foreign keys enforced (db.make_engine); the app uses Postgres.
- Docling is not wired in yet (its models download from Hugging Face); it is an A1 ablation option.
