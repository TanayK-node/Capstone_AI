# PaperLens

Not just what a paper says, but whether you can reproduce it. Every extracted fact links
back to the sentence it came from. See [SCOPE.md](SCOPE.md) for the full plan and
[CLAUDE.md](CLAUDE.md) for the working rules.

**Status: Phase 2 (grounded extraction).** Upload a PDF or paste a link; the pipeline parses
it into blocks with page coordinates, rebuilds results tables, labels sections, then asks
Gemini for a structured Overview (problem, contributions, method, datasets, hyperparameters,
compute, limitations, ...). Every item carries a verbatim quote; Python locates the quote in
the paper and a second check asks whether it supports the item. Click an evidence chip and
the PDF scrolls to the sentence and highlights it. Progress streams over server-sent events;
the Overview exports as JSON, Markdown, BibTeX or CSV.

Privacy: paper text is sent to the Gemini API free tier, whose inputs Google may use to
improve its models. Do not upload unpublished or confidential papers.

## Quick start

```bash
cp .env.example .env          # add GEMINI_API_KEY (free key from Google AI Studio)
docker compose up --build
```

- UI: http://localhost:3000 (upload / link box, library, paper workspace)
- API docs: http://localhost:8000/docs · health: http://localhost:8000/api/health
- GROBID: http://localhost:8070

### LLM provider

PaperLens runs on the Gemini API free tier only. The Ollama provider is still in the code but
switched off (`llm.fallback: null` in `config/config.yaml`). Without `GEMINI_API_KEY` the
health page shows "No LLM provider".

## Phase 2 exit check

With GROBID running and `GEMINI_API_KEY` in `.env`, from `backend/`:

```bash
uv run python -m app.pipeline.check_extract            # the 10 Phase 1 papers
uv run python -m app.pipeline.check_extract --limit 3  # fewer Gemini calls (~6 per paper)
uv run python -m app.pipeline.check_extract --pdf-dir ./pdfs
```

Per paper it reports pipeline time, items, and how many quotes were verified / partial /
unsupported / unlocated. A paper passes when it takes at most 3 minutes, every extraction call
succeeds, every item has a quote, and every located quote has boxes to highlight. The full
Overviews go to `data/phase2_check/report.md`.

## Phase 1 exit check

With GROBID running (`docker compose up grobid`), from `backend/`:

```bash
uv run python -m app.pipeline.check_parse            # downloads 10 arXiv papers and parses them
uv run python -m app.pipeline.check_parse --parser pymupdf   # same, without GROBID (ablation A1)
```

It prints one line per paper and `PHASE 1 EXIT CRITERION: PASS/FAIL` (target: all 10 parse,
tables found on at least 8). Every rebuilt table goes to `data/phase1_check/report.md` so you
can check the grids by eye.

## How parsing works

1. **Ingest** (`pipeline/ingest/`): the input is classified (arXiv, DOI, OpenReview, ACL,
   Semantic Scholar, PDF URL), the PDF downloaded and validated (PDF, at most 50 MB / 100 pages,
   must have a text layer), and stored under its SHA-256. The same PDF twice is one paper.
2. **Parse** (`pipeline/parse/`): GROBID gives structure, sentences, references and table
   locations, each with page coordinates. GROBID's table *grids* are unreliable, so tables are
   rebuilt from the PDF's word positions (`tables.py`): columns from whitespace gaps, wrapped
   cells merged, bold cells detected, numbers like `24.3 ± 0.2` parsed. If GROBID is down,
   a PyMuPDF-only parser takes over.
3. **Structure** (`pipeline/structure/`): sections get roles (method, experiments, results...)
   from heading rules; headings the rules can't place go to one batched Gemini call. Text is
   chunked section → paragraph → sentence, keeping coordinates.

## Development without Docker

```bash
# backend (Python 3.11 via uv)
cd backend
uv sync
uv run pytest                       # unit tests, no network
uv run pytest -m live               # real Gemini calls (Phase 0 exit criterion)
uv run python -m app.llm.check      # one toy call per provider
uv run python -m app.llm.check --list-models
uv run ruff check . && uv run ruff format --check . && uv run mypy app tests
uv run uvicorn app.main:app --reload  # needs Postgres/Redis: `docker compose up postgres redis grobid`
# No Redis/Celery (e.g. on Windows)? Set PAPERLENS_PIPELINE__EAGER=true to run the pipeline
# inside the API process. To use SQLite instead of Postgres:
# PAPERLENS_DATABASE_URL=sqlite:///./paperlens.db uv run alembic upgrade head

# frontend
cd frontend
pnpm install
pnpm dev
```

## Layout

| Path | What |
| --- | --- |
| `config/config.yaml` | Model names per role, rate limits, retry/fallback policy, feature flags. Env vars override any key (`PAPERLENS_LLM__PRIMARY=ollama`). |
| `config/checklist.yaml` | Reproducibility checklist (used from Phase 3) |
| `backend/app/llm/` | The single LLM gateway: `client.py` (cache, rate limit, retry, fallback, validation), `gemini.py`, `ollama.py`, `ratelimit.py`, `cache.py` |
| `backend/app/prompts/` | Versioned Jinja prompts (`{# version: N #}` header) |
| `backend/app/pipeline/` | Pipeline stages, one package per module M1 to M13 (ingest, parse, structure done) |
| `backend/tests/fixtures/` | Three generated test PDFs (+ their GROBID output); `make_fixtures.py` rebuilds them |
| `backend/alembic/` | Database migrations |
| `frontend/` | Next.js App Router UI |
| `eval/` | Gold set, benchmarks, ablations (Phase 6) |
| `sandbox/` | No-network image for static repo analysis (Phase 4) |

## Using the LLM gateway

```python
from app import prompts
from app.llm import get_llm_client

client = get_llm_client()
result = client.generate_json(prompts.render("toy_extract", text=paper_text), MySchema)
result.value        # validated MySchema instance
result.meta         # provider, model, prompt_version, cached, tokens, latency, fell_back
```

Every call is cached in Postgres (`llm_cache`), rate-limited per model (RPM and RPD from
config), retried with backoff on 429/5xx, and moved to Ollama when Gemini keeps failing or its
daily quota is spent (only if a fallback is configured). Invalid JSON gets one repair re-ask, then raises `LLMValidationError`.

## Privacy

Gemini free-tier inputs may be used by Google to improve its models. Don't upload confidential
manuscripts in Gemini mode; use offline mode instead.
