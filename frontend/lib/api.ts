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

export async function fetchHealth(signal?: AbortSignal): Promise<Health> {
  const res = await fetch(`${API_URL}/api/health`, { signal, cache: "no-store" });
  if (!res.ok) throw new Error(`health check failed: HTTP ${res.status}`);
  return res.json();
}
