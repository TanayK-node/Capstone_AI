# PaperLens

Not just what a paper says, but whether you can reproduce it. Every extracted fact links
back to the sentence it came from. See [SCOPE.md](SCOPE.md) for the full plan and
[CLAUDE.md](CLAUDE.md) for the working rules.

**Status: Phase 0 (skeleton).** Services, config, the LLM gateway and CI are in place; the
paper pipeline starts in Phase 1.

## Quick start

```bash
cp .env.example .env          # add GEMINI_API_KEY (free key from Google AI Studio)
docker compose up --build
```

- UI: http://localhost:3000 (shows service health and which LLM is active)
- API docs: http://localhost:8000/docs · health: http://localhost:8000/api/health
- GROBID: http://localhost:8070

### LLM provider

PaperLens runs on the Gemini API free tier only. The Ollama provider is still in the code but
switched off (`llm.fallback: null` in `config/config.yaml`). Without `GEMINI_API_KEY` the
health page shows "No LLM provider".

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
| `backend/app/pipeline/` | Pipeline stages, one package per module M1 to M13 (empty until Phase 1) |
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
