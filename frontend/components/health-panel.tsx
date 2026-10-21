"use client";

import { useEffect, useState } from "react";
import { fetchHealth, type Health } from "@/lib/api";

function Dot({ ok }: { ok: boolean }) {
  return (
    <span
      aria-hidden
      className={`inline-block h-2 w-2 rounded-full ${ok ? "bg-emerald-500" : "bg-amber-500"}`}
    />
  );
}

export function ProviderBadge({ llm }: { llm: Health["llm"] }) {
  const local = llm.active === "ollama";
  return (
    <span
      className={`rounded-full px-3 py-1 text-xs font-medium ${
        local
          ? "bg-amber-100 text-amber-900 dark:bg-amber-900/40 dark:text-amber-200"
          : "bg-sky-100 text-sky-900 dark:bg-sky-900/40 dark:text-sky-200"
      }`}
    >
      {llm.active === null ? "No LLM provider" : local ? "Running on local model" : "Gemini"}
    </span>
  );
}

export function HealthPanel() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const ctrl = new AbortController();
    const load = () =>
      fetchHealth(ctrl.signal)
        .then((h) => {
          setHealth(h);
          setError(null);
        })
        .catch((e: unknown) => {
          if (!ctrl.signal.aborted) setError(e instanceof Error ? e.message : String(e));
        });
    load();
    const id = setInterval(load, 10_000);
    return () => {
      ctrl.abort();
      clearInterval(id);
    };
  }, []);

  if (error) {
    return <p className="text-sm text-red-600">API unreachable: {error}</p>;
  }
  if (!health) {
    return <p className="text-sm text-zinc-500">Checking services…</p>;
  }

  return (
    <section className="w-full space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">System status</h2>
        <ProviderBadge llm={health.llm} />
      </div>
      <ul className="grid grid-cols-1 gap-2 sm:grid-cols-3">
        {Object.entries(health.services).map(([name, s]) => (
          <li
            key={name}
            className="flex items-center gap-2 rounded-lg border border-zinc-200 px-3 py-2 text-sm dark:border-zinc-800"
            title={s.error}
          >
            <Dot ok={s.ok} />
            <span className="capitalize">{name}</span>
          </li>
        ))}
      </ul>
      {health.llm.usage.length > 0 && (
        <table className="w-full text-left text-sm">
          <thead className="text-zinc-500">
            <tr>
              <th className="py-1">Model</th>
              <th>Used today</th>
              <th>Remaining</th>
            </tr>
          </thead>
          <tbody>
            {health.llm.usage.map((u) => (
              <tr key={`${u.provider}/${u.model}`}>
                <td className="py-1 font-mono">{u.model}</td>
                <td>{u.used_today}</td>
                <td>{u.remaining_today ?? "∞"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {health.llm.active === "gemini" && (
        <p className="text-xs text-zinc-500">
          Gemini free-tier inputs may be used by Google to improve its models. Don&apos;t upload
          confidential manuscripts in Gemini mode; switch to offline mode instead.
        </p>
      )}
    </section>
  );
}
