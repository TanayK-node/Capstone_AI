// Base URL of the FastAPI backend. Set NEXT_PUBLIC_API_URL to override.
export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type ServiceStatus = { ok: boolean; error?: string };

export type ModelUsage = {
  provider: string;
  model: string;
  rpm: number | null;
  rpd: number | null;
  used_today: number;
  remaining_today: number | null;
};

// Mirrors the backend /api/health response (app/api/health.py).
export type Health = {
  status: "ok" | "degraded";
  services: Record<string, ServiceStatus>;
  llm: {
    primary: string;
    fallback: string | null;
    active: string | null;
    degraded: boolean;
    configured: string[];
    consecutive_failures: number;
    usage: ModelUsage[];
  };
};

// ---- papers (mirrors app/api/papers.py)

// "partial": parsed fine, but an analysis stage (extract / verify) failed.
export type PaperStatus = "queued" | "processing" | "ready" | "partial" | "failed";

export type PaperSummary = {
  id: string;
  title: string | null;
  source_type: string;
  source_id: string | null;
  status: PaperStatus;
  page_count: number;
  created_at: string;
};

export type StageStatus = {
  status: "queued" | "running" | "done" | "failed";
  error: string | null;
  started_at: string | null;
  finished_at: string | null;
  provider: string | null;
  model: string | null;
  prompt_version: string | null;
  detail: Record<string, unknown>;
};

export type SectionNode = {
  id: string;
  title: string;
  path: string[];
  depth: number;
  role: string;
  role_source: string;
  page: number;
  block_ids: string[];
  children: string[];
};

export type PaperDetail = PaperSummary & {
  source_url: string | null;
  error: string | null;
  metadata: Record<string, unknown>;
  stages: Record<string, StageStatus>;
  parse: {
    parser: string;
    parser_version: string;
    warnings: string[];
    metadata: { title?: string | null; authors?: { name: string }[]; abstract?: string | null };
    sections: SectionNode[];
    block_counts: Record<string, number>;
    reference_count: number;
  } | null;
};

export type Box = { page: number; x0: number; y0: number; x1: number; y1: number };

export type TableCell = {
  text: string;
  row: number;
  col: number;
  value: number | null;
  std: number | null;
  is_percent: boolean;
  is_bold: boolean;
  is_header: boolean;
};

export type TableData = {
  label: string | null;
  caption: string;
  n_rows: number;
  n_cols: number;
  header_rows: number;
  cells: TableCell[];
};

export type Block = {
  id: string;
  type: string;
  order: number;
  page: number;
  bbox: Box | null;
  boxes: Box[];
  section_path: string[];
  role: string | null;
  label: string | null;
  text: string;
  table: TableData | null;
};

export type PageInfo = { number: number; width: number; height: number };

export type BlocksResponse = { pages: PageInfo[]; blocks: Block[] };

export type CreatePaperResponse = {
  paper_id: string;
  status: PaperStatus;
  duplicate: boolean;
  dispatched_to: string | null;
};

// ---- extraction (mirrors app/schemas/extraction.py)

export type GroundingStatus = "verified" | "partial" | "unlocated" | "unsupported" | "unchecked";

export type Evidence = {
  chunk_id: string;
  page: number;
  bbox: Box | null;
  boxes: Box[];
  quote: string;
  grounding_status: GroundingStatus;
  match_score: number | null;
};

export type Item = {
  id: string;
  value: string;
  evidence: Evidence[];
  confidence: number;
  source: "llm" | "rule";
  // Dataset
  name?: string;
  split?: string;
  size?: string;
  public?: string;
  // Hyperparameter
  value_raw?: string;
  value_norm?: number | null;
  scope?: string;
  // Claim
  kind?: string;
};

export type ExtractionMetadata = {
  title: string | null;
  authors: string[];
  venue: string | null;
  year: string | null;
  arxiv_id: string | null;
  doi: string | null;
  urls: string[];
};

export const ITEM_FIELDS = [
  "problem",
  "task",
  "contributions",
  "method_summary",
  "novelty",
  "datasets",
  "baselines",
  "metrics",
  "hyperparameters",
  "compute",
  "seeds_and_runs",
  "ablations",
  "claims",
  "limitations",
  "future_work",
  "ethics",
  "code_urls",
] as const;
export type ItemField = (typeof ITEM_FIELDS)[number];

export type PaperExtraction = { metadata: ExtractionMetadata; results: unknown[] } & {
  [K in ItemField]: Item[];
};

export type ExtractionResponse = {
  paper_id: string;
  verified: boolean;
  grounding_score: number | null;
  provider: string | null;
  model: string | null;
  prompt_version: string | null;
  created_at: string;
  status_counts: Partial<Record<GroundingStatus, number>>;
  data: PaperExtraction;
};

export type ExportFormat = "json" | "md" | "bib" | "csv";

// ---- results tables (mirrors app/schemas/results.py)

export type ResultColumn = {
  index: number;
  header: string;
  group: string;
  numeric: boolean;
  higher_is_better: boolean | null;
};

export type ResultCell = {
  col: number;
  text: string;
  value: number | null;
  std: number | null;
  is_percent: boolean;
  is_bold: boolean;
  is_best: boolean;
};

export type ResultRow = {
  index: number;
  label: string;
  group: string;
  is_proposed: boolean;
  cells: ResultCell[];
};

export type ResultsTable = {
  table_id: string;
  label: string | null;
  caption: string;
  page: number;
  columns: ResultColumn[];
  rows: ResultRow[];
  proposed_names: string[];
};

// ---- claims (mirrors app/schemas/claims.py)

export type Verdict =
  "supported" | "contradicted" | "unsupported" | "weakly_supported" | "unverifiable";

export type CheckedCell = {
  table_id: string;
  table_label: string | null;
  row: number;
  col: number;
  row_label: string;
  column: string;
  text: string;
  value: number;
  role: "method" | "baseline";
};

export type ClaimCheck = {
  id: string;
  text: string;
  evidence: Evidence[];
  kind: "score" | "improvement" | "factor" | "qualitative";
  method: string;
  baseline: string;
  dataset: string;
  metric: string;
  comparator: string;
  direction: string;
  claimed_value: number | null;
  claimed_delta: number | null;
  delta_unit: string;
  table_value: number | null;
  baseline_value: number | null;
  recomputed_delta: number | null;
  recomputed_relative: number | null;
  recomputed_factor: number | null;
  verdict: Verdict;
  explanation: string;
  checked_cells: CheckedCell[];
};

export type ClaimsResponse = {
  paper_id: string;
  provider: string | null;
  model: string | null;
  prompt_version: string | null;
  created_at: string;
  report: {
    tolerance: number;
    claims: ClaimCheck[];
    counts: Partial<Record<Verdict, number>>;
    warnings: string[];
  };
};

// ---- reproducibility (mirrors app/schemas/repro.py)

export type ItemStatus = "present" | "partial" | "missing" | "not_applicable" | "unknown";

export type ChecklistResult = {
  id: string;
  group: string;
  description: string;
  weight: number;
  status: ItemStatus;
  source: "rule" | "extraction" | "repo" | "llm" | "none";
  note: string;
  evidence: Evidence[];
  question: string;
};

export type GroupScore = {
  id: string;
  label: string;
  weight: number;
  score: number | null;
  counts: Partial<Record<ItemStatus, number>>;
};

export type RepoInfo = {
  url: string;
  host: string;
  owner: string | null;
  name: string | null;
  reachable: boolean | null;
  license: string | null;
  stars: number | null;
  pushed_at: string | null;
  archived: boolean | null;
  root_files: string[];
  error: string | null;
};

export type Scorecard = {
  checklist_version: number;
  score: number | null;
  groups: GroupScore[];
  items: ChecklistResult[];
  missing: string[];
  questions: string[];
  repo: RepoInfo | null;
  warnings: string[];
};

export type ReproResponse = {
  paper_id: string;
  score: number | null;
  checklist_version: number;
  provider: string | null;
  model: string | null;
  prompt_version: string | null;
  created_at: string;
  scorecard: Scorecard;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { cache: "no-store", ...init });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      // body was not JSON; keep the status line
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const fetchHealth = (signal?: AbortSignal) => request<Health>("/api/health", { signal });
export const listPapers = () => request<PaperSummary[]>("/api/papers");
export const getPaper = (id: string) => request<PaperDetail>(`/api/papers/${id}`);
export const getBlocks = (id: string) => request<BlocksResponse>(`/api/papers/${id}/blocks`);
export const pdfUrl = (id: string) => `${API_URL}/api/papers/${id}/pdf`;
export const getExtraction = (id: string) =>
  request<ExtractionResponse>(`/api/papers/${id}/extraction`);
export const getReproducibility = (id: string) =>
  request<ReproResponse>(`/api/papers/${id}/reproducibility`);
export const getTables = (id: string) => request<ResultsTable[]>(`/api/papers/${id}/tables`);
export const tablesCsvUrl = (id: string) => `${API_URL}/api/papers/${id}/tables?format=csv`;
export const getClaims = (id: string) => request<ClaimsResponse>(`/api/papers/${id}/claims`);
export const exportUrl = (id: string, format: ExportFormat) =>
  `${API_URL}/api/papers/${id}/export?format=${format}`;
/** Server-sent events: `stage` per stage status change, `status`, then `done`. */
export const eventsUrl = (id: string) => `${API_URL}/api/papers/${id}/events`;

/** Upload a PDF file or submit a link (arXiv id/URL, DOI, OpenReview, ACL, PDF URL). */
export function createPaper(input: { file: File } | { url: string }) {
  const form = new FormData();
  if ("file" in input) form.append("file", input.file);
  else form.append("url", input.url);
  return request<CreatePaperResponse>("/api/papers", { method: "POST", body: form });
}

export const rerunPaper = (id: string, stages?: string[]) =>
  request<CreatePaperResponse>(`/api/papers/${id}/rerun`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(stages ? { stages } : {}),
  });
