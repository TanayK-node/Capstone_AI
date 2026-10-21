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

export type PaperStatus = "queued" | "processing" | "ready" | "failed";

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

/** Upload a PDF file or submit a link (arXiv id/URL, DOI, OpenReview, ACL, PDF URL). */
export function createPaper(input: { file: File } | { url: string }) {
  const form = new FormData();
  if ("file" in input) form.append("file", input.file);
  else form.append("url", input.url);
  return request<CreatePaperResponse>("/api/papers", { method: "POST", body: form });
}

export const rerunPaper = (id: string) =>
  request<CreatePaperResponse>(`/api/papers/${id}/rerun`, { method: "POST" });
