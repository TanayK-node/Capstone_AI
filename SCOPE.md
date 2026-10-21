# PaperLens — Research Paper Information Extractor: Scope Document

Oct 21, 2026 · @tanay

## 1. Overview

PaperLens takes a research paper (PDF upload or link) and returns a grounded, structured breakdown of what it claims, how it did it, and whether someone could actually reproduce it. The working name is a placeholder; rename freely.

**One-line pitch:** not just what the paper says, but whether you can reproduce it, with every extracted fact linked back to the exact sentence it came from.

### Problem

- Reading a paper well takes 1 to 3 hours. Most of that time goes to hunting for the same things: datasets, baselines, hyperparameters, results, limitations.
- Reproducibility is poor across ML. Papers omit seeds, compute, variance and exact configs, and released code often disagrees with the paper.
- Existing summarizers produce fluent prose with no evidence. That is unusable for research, where a hallucinated number is worse than no number.

### Target users

- Students and researchers doing literature review or planning a reproduction.
- Reviewers who want a fast checklist pass.
- Course evaluators: the demo must work live on any arXiv paper they pick.

### What the system does (end to end)

1. Accepts a PDF upload or a link (arXiv, DOI, OpenReview, ACL Anthology, Semantic Scholar, direct PDF URL).
2. Parses it with layout awareness into sections, paragraphs, tables, figures, equations and references, keeping page and bounding-box coordinates.
3. Extracts a fixed schema (problem, contributions, method, datasets, baselines, metrics, results, hyperparameters, compute, limitations) where every field carries evidence spans.
4. Scores reproducibility against a checklist and lists what is missing.
5. Finds the code repository, statically analyzes it, and flags mismatches between paper and code.
6. Verifies headline claims against the parsed results tables.
7. Offers grounded chat, multi-paper comparison, a citation graph and a reviewer-style critique.
8. Shows everything in a UI with the PDF beside the extraction; clicking any field highlights its source in the PDF.

### Success criteria

| Criterion | Target |
| --- | --- |
| Field-level extraction F1 on the gold set | ≥ 0.80 for core fields |
| Grounding accuracy (cited span supports the field) | ≥ 0.90 |
| Reproducibility checklist agreement with human annotators | Cohen's κ ≥ 0.6 |
| End-to-end time for a 12-page paper on Gemini free tier | ≤ 3 minutes |
| Works fully offline with local Qwen | Yes, with documented quality drop |
| Live demo on an unseen arXiv paper | No crashes; partial results stream in |

These targets are proposals for the team to adjust after the first evaluation run.

## 2. Constraints and model strategy

The only LLMs available are the Gemini API free tier and a local Qwen model on a laptop, so the whole design minimizes LLM calls and never depends on one provider. Deterministic code does everything it can (parsing, regex, table parsing, repo analysis); the LLM only does what needs language understanding.

### Providers

| Role | Primary | Fallback | Notes |
| --- | --- | --- | --- |
| Structured extraction, claims, critique | Gemini Flash (free tier) | Local Qwen via Ollama | Long context lets one call see a whole section group |
| High-volume small calls (classification, field checks) | Gemini Flash-Lite (free tier) | Local Qwen small | Higher free quota than Flash |
| Figure / chart reading | Gemini Flash (multimodal) | Qwen VL model via Ollama, or skip | Stretch feature only |
| Embeddings for RAG chat | Local sentence-transformers (e.g. bge-small or all-MiniLM) | Gemini embedding model | Local embeddings keep chat free and offline |
| Offline mode | Qwen3 / Qwen3.5 8B-class, Q4 quantized via Ollama | Smaller Qwen (1.7B to 4B) on weak laptops | 8B-class at Q4 needs roughly 16 GB RAM or 8 GB VRAM |

As of October 2026, the free tier covers Gemini's Flash and Flash-Lite models; Pro-tier availability on the free tier has changed during 2026 and is not to be relied on. Free-tier limits sit at roughly 10 to 15 requests per minute and on the order of hundreds to about 1,500 requests per day per model, applied per project, and they change without notice. Free-tier inputs may be used by Google to improve its models, so the UI must warn users not to upload confidential manuscripts in Gemini mode.

### Design rules that follow from the constraints

1. **Every model name lives in config** (`config.yaml` / env vars). Nothing hardcodes a model ID, because free-tier model lineups change several times a year.
2. **One LLM abstraction** (`llm/client.py`) with `generate_json(prompt, schema)` and `generate_text(prompt)`. Implementations: `GeminiClient`, `OllamaClient`. LiteLLM is acceptable as the underlying router.
3. **Rate limiter + retry:** token-bucket per model (RPM and RPD), exponential backoff with jitter on HTTP 429, automatic fallback to Ollama after N failures, and a visible "running on local model" badge in the UI.
4. **Cache everything:** key = hash(PDF bytes + prompt version + model). Re-running a paper costs zero calls. Store cache in SQLite or Postgres.
5. **Call budget per paper:** target ≤ 15 LLM calls for the core pipeline. Batch fields per section group instead of one call per field.
6. **Schema-constrained output:** Gemini's JSON response mode with a Pydantic-derived schema; Ollama's `format` JSON-schema option for Qwen. Validate with Pydantic and re-ask once on failure.
7. **Thinking mode off by default** for Qwen and Flash on extraction calls; on only for claim verification and critique, where reasoning helps.
8. **Model-agnostic evaluation:** every experiment records provider, model and prompt version, so Gemini vs. Qwen becomes an ablation, not a problem.

### Context-length strategy

A 12-page paper is roughly 10k to 15k tokens. Gemini Flash can take the whole paper in one call, but a local 8B model should get section groups (abstract + intro, method, experiments, appendix) of ≤ 8k tokens. The extractor works per section group in both modes so outputs are comparable, then a merge step reconciles fields.

## 3. Feature scope

All features stay in scope, split into three tiers. The tiers set build order, not importance. Tier 1 must be demo-ready before any Tier 2 work starts.

| ID | Feature | Tier | What the user sees |
| --- | --- | --- | --- |
| F1 | Multi-source ingestion | 1 | Upload PDF or paste arXiv / DOI / OpenReview / ACL / Semantic Scholar / PDF link; metadata card fills in |
| F2 | Layout-aware parsing | 1 | Section tree, tables, figures, equations, references, all with page + bbox |
| F3 | Grounded structured extraction | 1 | Summary cards per schema field, each with clickable evidence |
| F4 | PDF evidence viewer | 1 | Click a field → PDF scrolls to and highlights the source span |
| F5 | Reproducibility scorecard | 1 | Checklist with present / partial / missing, evidence, overall score, "missing for reproduction" list |
| F6 | Export | 1 | JSON, Markdown report, BibTeX, results CSV |
| F7 | Paper–code consistency check | 2 | Repo health card + table of paper value vs. code value with match / mismatch / not found |
| F8 | Claim–evidence verification | 2 | Each headline claim with verdict: supported / unsupported / contradicted / unverifiable, plus the table cell it was checked against |
| F9 | Results table extraction | 2 | Clean, editable results tables; download as CSV |
| F10 | Grounded chat with the paper | 2 | Q&A where every answer cites section and page |
| F11 | Equation and notation glossary | 2 | LaTeX equations + symbol table; hover a symbol to see its definition |
| F12 | Repro Kit generator | 3 | Downloadable zip: environment.yml / Dockerfile guess, run plan, expected numbers, compute estimate |
| F13 | Citation graph and context | 3 | Key references, influential citing papers, novelty positioning summary |
| F14 | Multi-paper comparison matrix | 3 | Upload 2 to 10 papers → method × dataset × metric matrix |
| F15 | Reviewer mode | 3 | OpenReview-style review: summary, strengths, weaknesses, missing ablations, questions |
| F16 | Chart-to-data | 3 | Plot images converted to approximate data tables |
| F17 | Audience-level summaries | 3 | TL;DR, student explanation, expert summary |

### Detailed behavior of the headline features

**F3 – Grounded extraction.** Every field value is a list of items, and every item carries `evidence: [{chunk_id, page, bbox, quote}]`. A post-hoc grounding verifier checks each quote exists in the parsed text (fuzzy match ≥ 0.9) and that it supports the value (small NLI-style LLM check, batched). Items failing either check are shown with an "unverified" badge rather than dropped, and the failure count feeds the hallucination metric.

**F5 – Reproducibility scorecard.** About 20 checklist items derived from the NeurIPS paper checklist and the ML Reproducibility Challenge, grouped into Code, Data, Experimental setup, Compute, and Statistical reporting. Each item is filled by a rule (regex or structure check) first and an LLM check only if the rule is inconclusive. Score = weighted sum, shown as 0 to 100 with a per-group breakdown. Items marked "missing" become the "missing for reproduction" list.

**F7 – Paper–code consistency.** Finds repo links in the paper (footnotes, abstract, URLs) or via the Papers with Code successor data on Hugging Face if available. Clones shallowly into a sandbox, never executes repo code, and parses YAML/JSON configs, argparse/Hydra/click defaults, and README commands. Matches hyperparameter names fuzzily (lr ↔ learning\_rate) and compares values with unit/format normalization (3e-4 = 0.0003). Repo health: license, requirements/environment file, README run instructions, last commit date, stars, open issues containing "reproduce" (GitHub API, unauthenticated or with a personal token).

**F8 – Claim verification.** Extracts quantitative claims from abstract, intro and conclusion ("improves accuracy by 4.2% over X on Y"). Each claim is parsed into `{metric, dataset, method, baseline, delta, direction}`, then matched to the parsed results tables, and the delta is recomputed in Python (not by the LLM). Verdicts are computed deterministically from the recomputed numbers with a tolerance (±0.15 absolute).

## 4. System architecture

PaperLens is a three-tier app (Next.js UI, FastAPI API, Celery worker pipeline) on one Postgres database, with every LLM call routed through a single gateway that handles rate limits, caching and Gemini-to-Qwen fallback.

The API only enqueues jobs and reads results; all heavy work runs in the worker, and the four analysis stages after Verify run in parallel.

### Tech stack

| Layer | Choice | Why |
| --- | --- | --- |
| Frontend | Next.js (App Router), TypeScript, Tailwind, shadcn/ui | Fast to build, good component library |
| PDF viewer | react-pdf (PDF.js) with custom highlight layer | Needs bbox-level highlights |
| State / data | TanStack Query, EventSource for SSE | Simple live progress |
| Graphs | react-force-graph or Cytoscape.js | Citation graph |
| API | FastAPI, Pydantic v2 | Typed schemas shared with LLM outputs |
| Jobs | Celery + Redis | Long-running stages, retries, parallel stages |
| Database | PostgreSQL 16 + pgvector, SQLAlchemy 2, Alembic | One store for metadata, JSON results and embeddings |
| Parsing | GROBID (Docker), Docling, PyMuPDF; optional Nougat/Marker | Structure, tables, coordinates |
| LLM | google-genai SDK, Ollama, optional LiteLLM | Free tier + offline |
| Retrieval | sentence-transformers, rank\_bm25, optional cross-encoder | Local, free |
| Code analysis | GitPython, Python `ast`, PyYAML, GitHub REST API | Static only |
| Packaging | Docker Compose; uv or poetry; pnpm | One-command start |
| Quality | pytest, ruff, mypy, eslint, prettier, GitHub Actions | CI from day one |

### Data flow for one paper

1. UI posts a file or link → API stores the PDF, creates a paper record and a job, returns IDs.
2. UI opens the SSE stream for the job.
3. Worker runs Ingest → Parse → Chunk → Extract → Verify, saving each stage's output and emitting an event.
4. Worker fans out Repro score, Code check, Claims and Chat index in parallel.
5. UI renders each tab as its event arrives; any failed stage shows an error card with a retry button.

### Repository layout

```
paperlens/
├── CLAUDE.md
├── SCOPE.md                  # this document, exported
├── docker-compose.yml
├── .env.example
├── config/
│   ├── config.yaml           # model names, rate limits, feature flags
│   └── checklist.yaml        # reproducibility checklist
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/              # routers per resource
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas (single source of truth)
│   │   ├── llm/              # client.py, gemini.py, ollama.py, ratelimit.py, cache.py
│   │   ├── prompts/          # *.jinja, versioned
│   │   ├── pipeline/
│   │   │   ├── ingest/
│   │   │   ├── parse/
│   │   │   ├── structure/
│   │   │   ├── extract/
│   │   │   ├── verify/
│   │   │   ├── repro/
│   │   │   ├── code_check/
│   │   │   ├── claims/
│   │   │   ├── tables/
│   │   │   ├── math/
│   │   │   ├── chat/
│   │   │   ├── context/
│   │   │   └── generate/
│   │   ├── workers/          # Celery app and task wiring
│   │   └── utils/
│   ├── alembic/
│   └── tests/
│       └── fixtures/         # 3 small test PDFs
├── frontend/
│   ├── app/
│   ├── components/
│   │   ├── pdf/              # viewer + highlight layer
│   │   └── tabs/             # overview, repro, code, claims, results, math, chat, context, review
│   └── lib/
├── eval/
│   ├── ANNOTATION_GUIDE.md
│   ├── gold/                 # annotated JSON
│   ├── benchmarks/           # SciREX, Qasper loaders
│   ├── run_eval.py
│   └── ablations/
└── sandbox/
    └── Dockerfile            # no-network container for repo analysis
```

## 5. Pipeline modules in depth

The pipeline is a sequence of independent stages, each reading and writing typed objects to the database, so any stage can be re-run, cached or swapped for an ablation. Stages after parsing run in parallel where they don't depend on each other.

### M1 – Ingestion (`ingest/`)

- Input resolver: classify input as file, arXiv ID/URL, DOI, OpenReview, ACL Anthology, Semantic Scholar, or direct PDF URL.
- arXiv: use the arXiv API for metadata and the PDF link; also fetch the LaTeX source tarball when available (gives exact equations and tables, a big accuracy win).
- DOI: resolve via Crossref / Unpaywall for an open-access PDF; if none, ask the user to upload.
- Semantic Scholar Graph API: metadata, references, citations, `openAccessPdf`.
- Store: SHA-256 of PDF bytes as the paper's identity (dedupe + cache key).
- Validation: PDF only, max 50 MB, max 100 pages; reject scanned PDFs without a text layer unless OCR is enabled.

### M2 – Parsing (`parse/`)

- Pluggable parsers behind one interface `parse(pdf) -> ParsedDocument`:
  - **GROBID** (Docker) – header metadata, section structure, references as TEI XML, with coordinates. Default for structure.
  - **Docling** – layout analysis and table structure. Default for tables.
  - **PyMuPDF** – fast text with exact character bboxes; used to map any quote back to coordinates.
  - **Nougat or Marker** (optional) – math-heavy papers; ablation only, since they are slow on CPU.
- Output: `ParsedDocument` with blocks (paragraph, heading, table, figure, caption, equation, footnote, reference), each with `page`, `bbox`, `section_path`, `text`.
- Table normalization: header detection, merged cells, bold-best-value detection, numeric parsing with ± and % handling.
- If LaTeX source exists, prefer its tables and equations and align them to PDF blocks by text similarity.

### M3 – Structuring and chunking (`structure/`)

- Build a section tree; classify each section into canonical roles (abstract, introduction, related work, method, experiments, results, ablation, limitations, conclusion, appendix) with heuristics + a small LLM call for ambiguous headings.
- Hierarchical chunks: section → paragraph → sentence, each chunk keeps parent IDs and coordinates.
- Index chunks in the vector store (local embeddings) and a BM25 index for hybrid retrieval.

### M4 – Structured extraction (`extract/`)

- One extractor per section group, each with a focused prompt and a JSON schema subset:
  - Abstract + intro → problem, contributions, task, claims.
  - Method → approach, architecture, key equations, novelty.
  - Experiments → datasets, baselines, metrics, hyperparameters, compute, seeds, runs.
  - Results + tables → main results, ablations.
  - Limitations + conclusion → limitations, future work, ethics.
- Prompts require each item to quote its source sentence verbatim; the quote is the evidence.
- Merge step: deduplicate entities across groups (e.g. "ImageNet-1k" = "ImageNet"), resolve conflicts by preferring Experiments over Abstract for numbers.
- Optional rule-based pre-extractors (regex for lr, batch size, epochs, GPU models, "seed") whose hits are given to the LLM as hints and also used in ablation.

### M5 – Grounding verifier (`verify/grounding.py`)

1. Locate each quote in parsed text with fuzzy matching (rapidfuzz partial ratio); map to page + bbox via PyMuPDF search.
2. If not found → status `unlocated`.
3. If found → batched entailment check ("does this quote support this value? yes/no/partial") with Flash-Lite or local Qwen.
4. Store per-item `grounding_status` and aggregate a per-paper grounding score.

### M6 – Reproducibility analyzer (`repro/`)

- Checklist defined in `repro/checklist.yaml` (item id, group, weight, description, rule hints).
- Rule layer: regex/structure checks (e.g. a table with ± or std, the words seed / random seed, GPU model names, "hours", a GitHub URL, dataset links).
- LLM layer: only for items the rule layer marks inconclusive; returns status + evidence.
- Pulls in M7 results for code-related items.
- Outputs score, per-group breakdown, missing list, and suggested author questions.

### M7 – Code analyzer (`code_check/`)

- Repo discovery: paper text URLs → Semantic Scholar / Hugging Face papers links → GitHub search by title (with confidence score; ask the user to confirm low-confidence matches).
- Shallow clone (`--depth 1`) into a temp dir inside a Docker container with no network after clone, size cap 200 MB, timeout 60 s. Never runs `setup.py`, notebooks or scripts.
- Static extraction: YAML/JSON/TOML configs, Python AST for argparse `add_argument` defaults, Hydra configs, click options, constants named like hyperparameters, README code blocks.
- Comparison: normalize names (synonym table + embedding similarity) and values; produce match / mismatch / only-in-paper / only-in-code rows.
- Health card via GitHub REST API (rate-limited; optional personal token in env).

### M8 – Claim verifier (`claims/`)

- LLM extracts quantitative claims into a structured form.
- Python locates the matching table cells (dataset and metric names fuzzy-matched to table headers, method names to row labels).
- Python recomputes deltas (absolute and relative) and assigns verdicts; the LLM never does arithmetic.
- Qualitative claims ("state of the art") are checked only for the presence of a comparison table and marked `weakly supported` or `unverifiable`.

### M9 – Tables and figures (`tables/`, `figures/`)

- Results tables: typed cells, best-value detection, export to CSV.
- Figures: crop images with captions; chart-to-data via Gemini multimodal (stretch); always labeled "approximate".

### M10 – Equations and glossary (`math/`)

- Equations from LaTeX source or Nougat output; otherwise images with captions.
- LLM builds a symbol table from the method section: symbol, meaning, first-defined location.

### M11 – Grounded chat (`chat/`)

- Hybrid retrieval (BM25 + embeddings), rerank top 20 with a cross-encoder (local, e.g. bge-reranker-base) or skip on weak hardware, top 5 to the LLM.
- Answer must cite chunk IDs; UI renders citations as clickable page links. Refuses when retrieval finds nothing relevant.
- Multi-paper mode searches across papers in a user's collection.

### M12 – Context and citation graph (`context/`)

- Semantic Scholar: references, citations, influential citations, venues.
- Graph view of top 20 references and top 20 citing papers.
- Novelty positioning: LLM compares the paper's contributions against abstracts of its 10 most-cited references.

### M13 – Generators (`generate/`)

- Repro Kit: environment file guessed from code imports and paper-stated versions; run plan from README + paper; expected results table; compute estimate from paper-stated hardware and hours.
- Reviewer mode: structured review prompt fed with extraction + scorecard + claim verdicts, so the critique is grounded in earlier findings.
- Comparison matrix: built from stored extractions; no new LLM calls except entity normalization.
- Audience summaries: three-level summary from the extraction JSON.

## 6. Data models and extraction schema

Pydantic models are the single source of truth: they generate the LLM JSON schemas, the API response types, and (via a codegen step) the frontend TypeScript types.

### Core extraction schema (Pydantic, abbreviated)

```python
class Evidence(BaseModel):
    chunk_id: str
    page: int
    bbox: tuple[float, float, float, float] | None
    quote: str                      # verbatim sentence from the paper
    grounding_status: Literal["verified", "partial", "unlocated", "unsupported"] = "unlocated"

class Item(BaseModel):
    value: str
    evidence: list[Evidence]
    confidence: float               # model-reported, calibrated later

class Dataset(Item):
    name: str; split: str | None; size: str | None; url: str | None; public: bool | None

class Hyperparameter(Item):
    name: str; value_raw: str; value_norm: float | str | None; scope: str | None  # e.g. "fine-tuning"

class ResultEntry(BaseModel):
    method: str; dataset: str; metric: str; value: float; std: float | None
    is_proposed: bool; table_id: str; cell: tuple[int, int]

class Claim(BaseModel):
    text: str; metric: str | None; dataset: str | None; baseline: str | None
    delta: float | None; direction: Literal["increase", "decrease"] | None
    verdict: Literal["supported", "unsupported", "contradicted", "weakly_supported", "unverifiable"] | None
    evidence: list[Evidence]; checked_cells: list[str]

class PaperExtraction(BaseModel):
    metadata: Metadata              # title, authors, venue, year, arxiv_id, doi, urls
    problem: list[Item]
    contributions: list[Item]
    task: list[Item]
    method_summary: list[Item]
    novelty: list[Item]
    datasets: list[Dataset]
    baselines: list[Item]
    metrics: list[Item]
    hyperparameters: list[Hyperparameter]
    compute: list[Item]             # hardware, GPU hours, training time
    seeds_and_runs: list[Item]
    results: list[ResultEntry]
    ablations: list[Item]
    limitations: list[Item]
    future_work: list[Item]
    ethics: list[Item]
    code_urls: list[Item]
    claims: list[Claim]
```

### Reproducibility checklist (initial items)

| Group | Items |
| --- | --- |
| Code | Code URL present · repo reachable · license · dependency file · run instructions · pretrained weights released |
| Data | All datasets named · datasets public or access described · preprocessing described · splits specified |
| Experimental setup | Hyperparameters for all models · hyperparameter search described · training details (optimizer, schedule, epochs) · evaluation protocol |
| Compute | Hardware type · training time or GPU hours · memory requirements |
| Statistical reporting | Number of runs / seeds · error bars or std · significance testing · results for baselines re-run vs. copied stated |

Each item has a weight (Code and Experimental setup weigh most), an optional rule, and a description used in the LLM prompt.

### Database tables (PostgreSQL)

| Table | Key columns |
| --- | --- |
| papers | id (sha256), source\_type, source\_url, title, metadata JSONB, status, created\_at |
| jobs | id, paper\_id, stage, status, error, started\_at, finished\_at, provider, model, prompt\_version |
| blocks | id, paper\_id, type, page, bbox, section\_path, text, order |
| chunks | id, paper\_id, block\_ids, level, text, embedding (pgvector) |
| extractions | paper\_id, version, data JSONB (PaperExtraction), model, prompt\_version |
| repro\_reports | paper\_id, score, groups JSONB, items JSONB |
| code\_reports | paper\_id, repo\_url, health JSONB, comparisons JSONB |
| claim\_reports | paper\_id, claims JSONB |
| llm\_cache | key (hash), provider, model, response, tokens, created\_at |
| collections | id, name, paper\_ids (for multi-paper comparison) |
| annotations | paper\_id, field, gold JSONB, annotator (gold set for evaluation) |

pgvector removes the need for a separate vector database. If pgvector is a problem on Windows, swap to ChromaDB behind the same interface.

## 7. API design and UI screens

The backend is a REST API with a server-sent-events stream per job, so the UI shows each stage's results as soon as they land instead of waiting for the whole pipeline.

### REST endpoints (FastAPI)

| Method | Path | Purpose |
| --- | --- | --- |
| POST | /api/papers | Upload PDF (multipart) or `{url}`; returns paper\_id + job\_id; dedupes by hash |
| GET | /api/papers | List papers in the library |
| GET | /api/papers/{id} | Metadata + stage statuses |
| GET | /api/jobs/{id}/events | SSE stream: stage\_started, stage\_done, partial\_result, error |
| GET | /api/papers/{id}/pdf | Serve the PDF to the viewer |
| GET | /api/papers/{id}/blocks | Parsed blocks with coordinates |
| GET | /api/papers/{id}/extraction | PaperExtraction JSON |
| GET | /api/papers/{id}/reproducibility | Scorecard |
| GET | /api/papers/{id}/code | Code report |
| POST | /api/papers/{id}/code/confirm | User confirms or supplies repo URL |
| GET | /api/papers/{id}/claims | Claim verdicts |
| GET | /api/papers/{id}/tables | Results tables; `?format=csv` |
| GET | /api/papers/{id}/glossary | Equations + symbols |
| POST | /api/papers/{id}/chat | `{question, history}` → streamed answer with citations |
| GET | /api/papers/{id}/graph | Citation graph |
| POST | /api/papers/{id}/review | Generate reviewer-mode critique |
| POST | /api/papers/{id}/repro-kit | Build and return zip |
| GET | /api/papers/{id}/export | `?format=json\|md\|bib` |
| POST | /api/papers/{id}/rerun | Re-run selected stages with a chosen provider |
| POST | /api/collections | Create a collection; GET /api/collections/{id}/matrix for comparison |
| GET | /api/settings | Provider status, rate-limit usage, offline mode toggle |

### UI screens (Next.js)

1. **Home / upload:** drop zone + link box, recent papers, provider badge (Gemini / Local Qwen) with remaining daily quota.
2. **Processing view:** stage timeline (Ingest → Parse → Extract → Verify → Reproducibility → Code → Claims) with live status; results cards appear as stages finish.
3. **Paper workspace (main screen):** split view. Left: PDF.js viewer with highlight overlays. Right: tabs:
   - **Overview:** metadata, TL;DR, problem, contributions, method, novelty, limitations. Each item has an evidence chip; click → PDF jumps and highlights.
   - **Reproducibility:** score gauge, group bars, checklist with statuses and evidence, "missing for reproduction" list, suggested questions to authors.
   - **Code:** repo health card, paper-vs-code table with match/mismatch coloring, confirm-repo prompt if low confidence.
   - **Claims:** claim list with verdict badges; expanding shows the table cells checked and the recomputed delta.
   - **Results:** extracted tables, editable, CSV download; charts-to-data in stretch.
   - **Math:** equations and symbol glossary.
   - **Chat:** grounded Q&A with citation chips.
   - **Context:** citation graph (react-force-graph or Cytoscape) and novelty summary.
   - **Review:** reviewer-mode output.
4. **Library / collections:** saved papers, multi-select → comparison matrix view.
5. **Evaluation dashboard (for the report and viva):** gold-set metrics, ablation tables, per-field F1 charts. Internal page, not linked from the main nav.
6. **Settings:** API key, model names, offline mode, rate-limit settings, cache clear.

### UX rules

- Every extracted claim is either evidenced or visibly marked unverified. No naked numbers.
- Partial results are always shown; one failed stage never blanks the page.
- Long jobs survive a page refresh (job state lives in the DB, UI reconnects to SSE).
- Dark mode, keyboard shortcuts for tab switching, and responsive layout down to tablet width.

## 8. Evaluation plan

Evaluation is a first-class deliverable: a hand-annotated gold set, public benchmarks for sub-tasks, and ablations that turn the free-tier vs. local-model constraint into a finding. An `eval/` package runs everything from one command and writes tables used directly in the report.

### Gold set

- 40 papers: 15 ML, 10 NLP, 10 CV, 5 from other areas (e.g. transportation ML) to test generalization. Mix of venues, years, and with/without code.
- 10 papers chosen from ML Reproducibility Challenge targets, so published reproduction reports give external ground truth on what was missing.
- Annotation: each team member annotates a share using an annotation page in the app (prefilled by the system, corrected by humans, with time logged). 8 papers double-annotated to report inter-annotator agreement.
- Annotation guide in `eval/ANNOTATION_GUIDE.md` defines each field and edge cases.

### Public benchmarks for sub-tasks

| Sub-task | Benchmark | Metric |
| --- | --- | --- |
| Dataset / task / metric / method extraction | SciREX (subset) | Entity-level F1 |
| Grounded QA (chat) | Qasper (subset of 100 questions) | Answer F1, evidence F1 |
| Table extraction | Results tables from the gold set (and PubTabNet-style samples if time allows) | Cell accuracy, structure accuracy |
| Reproducibility checklist | Gold set + MLRC reports | Per-item accuracy, Cohen's κ |

### Metrics

| Metric | Definition |
| --- | --- |
| Field F1 | Per schema field, fuzzy-matched item-level precision / recall / F1 |
| Numeric accuracy | Results and hyperparameters: exact after normalization |
| Grounding accuracy | Share of items whose evidence quote exists and supports the value (human-checked sample of 200) |
| Hallucination rate | Share of items with no locatable evidence or contradicting evidence |
| Checklist agreement | Accuracy and κ vs. human on present / partial / missing |
| Code-check precision | Share of flagged mismatches that are real (manual check) |
| Claim verdict accuracy | Verdict vs. human verdict on 100 claims |
| Cost and latency | LLM calls, tokens, wall-clock per paper, per provider |

### Ablations

| # | Variable | Settings |
| --- | --- | --- |
| A1 | Parser | GROBID vs. Docling vs. PyMuPDF-only vs. LaTeX-source |
| A2 | Extraction granularity | Whole paper in one call vs. per section group vs. per field |
| A3 | Grounding | No evidence requirement vs. quote required vs. quote + verifier |
| A4 | Rule hints | LLM only vs. regex hints + LLM |
| A5 | Model | Gemini Flash vs. Flash-Lite vs. Qwen 8B-class vs. Qwen small (offline) |
| A6 | Retrieval for chat | BM25 vs. dense vs. hybrid vs. hybrid + rerank |
| A7 | Claim verification | LLM judges verdict vs. Python recomputation |

A7 and A3 are expected to give the clearest results (deterministic verification and required evidence should cut hallucinations), and they make the strongest story for the report.

### Error analysis

Categorize at least 100 errors: parsing failure, retrieval miss, wrong entity normalization, hallucinated value, wrong table cell match, missing in paper (annotator disagreement). Report the distribution and two or three concrete examples per category.

## 9. Development phases

Build in eight phases (0 to 7), each ending in something demoable with its exit criteria met; no phase starts until the previous one passes. Calendar dates are not set yet; add them once the submission deadline is fixed.

1. **Phase 0 – Skeleton.** Monorepo, docker-compose (api, worker, postgres+pgvector, redis, grobid, frontend), config system, LLM client with Gemini + Ollama + rate limiter + cache, health endpoint, CI with lint + tests.
   - Exit: `docker compose up` works; a test calls both providers and gets valid JSON for a toy schema.
2. **Phase 1 – Ingest and parse.** M1, M2, M3. Upload and arXiv link work; blocks with bboxes stored; PDF viewer renders with a debug overlay of parsed blocks.
   - Exit: 10 arXiv papers parse without errors; tables detected on ≥ 8 of them.
3. **Phase 2 – Grounded extraction.** M4, M5, schema, Overview tab, click-to-highlight, SSE progress, export.
   - Exit: full Overview for any arXiv paper in ≤ 3 minutes; every item has an evidence chip that highlights correctly.
4. **Phase 3 – Reproducibility.** M6, checklist YAML, Reproducibility tab.
   - Exit: scorecard for the first 10 gold papers; team spot-checks agree on ≥ 80% of items.
5. **Phase 4 – Code and claims.** M7, M8, M9, Code, Claims and Results tabs.
   - Exit: correct repo found for ≥ 80% of papers that have code; at least one real paper–code mismatch demonstrated.
6. **Phase 5 – Chat, math, context.** M10, M11, M12, their tabs.
   - Exit: chat answers cite pages; glossary built for 5 math-heavy papers; graph renders.
7. **Phase 6 – Evaluation.** Gold set annotation, `eval/` runner, ablations A1 to A7, evaluation dashboard.
   - Exit: all metric tables generated by one command.
8. **Phase 7 – Stretch and polish.** M13 generators, chart-to-data, multi-paper matrix, audience summaries, UI polish, demo script, report.

Annotation for the gold set (Phase 6) should start in parallel from Phase 2, since it is the slowest human task.

## 10. Risks, non-goals and deliverables

The biggest risks are free-tier quota limits during the live demo and parser failures on unusual PDFs; both have fallbacks designed in.

### Risks and mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Gemini free-tier quota hit or model lineup changes | Pipeline stalls mid-demo | Cache, call budget ≤ 15 per paper, auto-fallback to Ollama, model names in config, pre-process demo papers the day before |
| Local Qwen too slow or weak on the laptop | Offline mode unusable | Section-group prompts ≤ 8k tokens, smaller Qwen variant, thinking off, report quality drop honestly as ablation A5 |
| Parsers fail on two-column, scanned or math-heavy PDFs | Bad blocks → bad extraction | Multiple parsers, LaTeX source for arXiv, PyMuPDF fallback, parse-quality warning in UI |
| Table structure errors | Wrong claim verdicts | Show checked cells to the user, mark low-confidence tables, prefer LaTeX tables |
| Repo not found or wrong repo matched | Misleading code report | Confidence score, user confirmation step, never assert a mismatch without showing both values |
| Security of cloning arbitrary repos | Malicious code | Static analysis only, no execution, sandbox container, size and time caps |
| Gold-set annotation takes longer than expected | Weak evaluation | Start annotating in Phase 2, prefilled annotation UI, cut gold set to 25 papers if needed |
| Scope creep from Tier 3 | Core features unfinished | Strict phase gates; Tier 3 only after Phase 6 |
| Free-tier data-use terms | Privacy concern for unpublished papers | UI warning in Gemini mode; offline mode for confidential PDFs |

### Non-goals

- Running or training the paper's models (the system analyzes; it does not execute experiments).
- Executing code from cloned repositories.
- Fine-tuning any LLM (possible future work if time remains: LoRA on Qwen with gold-set data).
- Full support for scanned PDFs without a text layer (OCR is optional).
- Multi-user auth and production deployment beyond a single-machine demo.

### Deliverables

- [ ] Source code repository with README, setup instructions and `docker compose up` one-command start
- [ ] Working web app with all Tier 1 and Tier 2 features, plus as many Tier 3 as time allows
- [ ] Offline mode running entirely on local Qwen
- [ ] Gold-set annotations (40 papers) and annotation guide
- [ ] Evaluation package with reproducible metric and ablation tables
- [ ] Project report (architecture, method, evaluation, error analysis, limitations)
- [ ] Demo video (5 minutes) and live demo script with 3 pre-chosen papers plus one evaluator-chosen paper
- [ ] Presentation slides
- [ ] Optional: workshop-paper draft built from the evaluation and ablation results

## Sources

Free-tier model availability and limits change often; re-check Google's official rate-limits and pricing pages before Phase 0.

- [Gemini API free tier limits (as of Sept 2026)](https://yingtu.ai/en/blog/google-gemini-api-free-tier-limits-2026)
- [Gemini API free tier: limits and rate quotas](https://tinkerllm.com/blog/gemini-api-free-tier-limits-rate-quotas/)
- [Gemini API pricing in 2026](https://geotoolbox.ai/blog/gemini-api-pricing.md)
- [Gemini API rate limits overview](https://www.developersdigest.tech/rate-limits/google)
- [Local LLMs in 2026: Qwen3.5 / Qwen3.6 lineup](https://mentorcruise.com/blog/local-llms-2-years-later-what-changed-whats-obsolete-what-to-run-instead-in-2026-821a/)
- [Ollama 2026 guide: hardware needs for 7B to 8B models](https://itsourcecode.com/ai-framework/ollama-run-local-llms-2026-complete-guide/)
