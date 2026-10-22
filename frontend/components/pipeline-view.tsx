"use client";

import { useEffect, useState } from "react";
import type { PaperDetail, StageStatus } from "@/lib/api";
import { StatusBadge } from "./status-badge";

// The stages in order, with what each one does (shown under its name).
const STAGES: { key: string; title: string; what: string }[] = [
  { key: "ingest", title: "Ingest", what: "fetch / receive the PDF, check it, store it" },
  { key: "parse", title: "Parse", what: "GROBID: text blocks with boxes, tables, references" },
  {
    key: "structure",
    title: "Structure",
    what: "section roles, section/paragraph/sentence chunks",
  },
  {
    key: "index",
    title: "Index",
    what: "embed passages locally for chat search (keyword search if no model)",
  },
  { key: "extract", title: "Extract", what: "one Gemini call per section group: items + quotes" },
  {
    key: "verify",
    title: "Verify",
    what: "find each quote in the paper, check it supports the item",
  },
  {
    key: "repro",
    title: "Reproducibility",
    what: "checklist: rules and GitHub first, Gemini for the rest; score",
  },
  {
    key: "claims",
    title: "Claims",
    what: "Gemini reads each claim; Python recomputes it from the tables",
  },
  {
    key: "code",
    title: "Code",
    what: "find the repo, clone it, scan it statically (never run), compare with the paper",
  },
  {
    key: "math",
    title: "Math",
    what: "equations from the LaTeX source (else the PDF); Gemini glossary, quotes grounded",
  },
  {
    key: "context",
    title: "Context",
    what: "references and citing papers (Semantic Scholar, else the PDF); Gemini novelty",
  },
];

const BAR_COLORS: Record<string, string> = {
  ingest: "#94a3b8",
  parse: "#2563eb",
  structure: "#7c3aed",
  extract: "#059669",
  verify: "#d97706",
  repro: "#db2777",
  claims: "#0891b2",
  code: "#4f46e5",
  index: "#0d9488",
  math: "#ca8a04",
  context: "#475569",
};

type GroupRun = {
  name: string;
  status: string;
  model: string | null;
  cached: boolean;
  items: number;
  truncated: boolean;
  error: string | null;
  seconds?: number;
  attempts?: number;
};

function seconds(stage: StageStatus | undefined, now: number): number | null {
  if (!stage?.started_at) return null;
  const start = Date.parse(stage.started_at);
  const end = stage.finished_at ? Date.parse(stage.finished_at) : now;
  return Math.max(0, (end - start) / 1000);
}

const fmt = (s: number | null) =>
  s === null ? "–" : s < 60 ? `${s.toFixed(1)}s` : `${Math.floor(s / 60)}m ${Math.round(s % 60)}s`;

export function PipelineView({ paper }: { paper: PaperDetail }) {
  const running = Object.values(paper.stages).some((s) => s.status === "running");
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    if (!running) return;
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, [running]);

  const times = STAGES.map((s) => seconds(paper.stages[s.key], now) ?? 0);
  // Ingest includes the download, which the 3-minute target does not count.
  const pipelineTotal = times.slice(1).reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-4">
      <section className="space-y-2">
        <div className="flex items-baseline justify-between text-xs text-zinc-500">
          <span>Time per stage</span>
          <span>
            parse → verify: <b className="text-zinc-800 dark:text-zinc-200">{fmt(pipelineTotal)}</b>
            {pipelineTotal > 180 && <span className="ml-1 text-amber-600">(over 3 min)</span>}
          </span>
        </div>
        <div className="flex h-3 overflow-hidden rounded bg-zinc-100 dark:bg-zinc-800">
          {STAGES.map((s, i) =>
            times[i] > 0 ? (
              <div
                key={s.key}
                title={`${s.title}: ${fmt(times[i])}`}
                style={{ flexGrow: times[i], background: BAR_COLORS[s.key] }}
              />
            ) : null,
          )}
        </div>
        <div className="flex flex-wrap gap-x-3 text-[11px] text-zinc-500">
          {STAGES.map((s, i) => (
            <span key={s.key} className="flex items-center gap-1">
              <span
                className="inline-block h-2 w-2 rounded-sm"
                style={{ background: BAR_COLORS[s.key] }}
              />
              {s.title} {fmt(times[i] || null)}
            </span>
          ))}
        </div>
      </section>

      <ol className="space-y-3">
        {STAGES.map((s, i) => {
          const stage = paper.stages[s.key];
          return (
            <li
              key={s.key}
              className="rounded-lg border border-zinc-200 p-3 dark:border-zinc-800"
              style={{ borderLeft: `4px solid ${BAR_COLORS[s.key]}` }}
            >
              <div className="flex items-center justify-between gap-2">
                <div>
                  <span className="font-medium">
                    {i + 1}. {s.title}
                  </span>
                  <span className="ml-2 text-xs text-zinc-500">{s.what}</span>
                </div>
                <div className="flex shrink-0 items-center gap-2 text-xs">
                  <span className="text-zinc-500">{fmt(seconds(stage, now))}</span>
                  <StatusBadge status={stage?.status ?? "queued"} />
                </div>
              </div>
              {stage && (stage.provider || stage.model || stage.prompt_version) && (
                <p className="mt-1 text-[11px] text-zinc-500">
                  {[stage.provider, stage.model].filter(Boolean).join(" · ")}
                  {stage.prompt_version && ` · prompts ${stage.prompt_version}`}
                </p>
              )}
              {stage?.error && (
                <p className="mt-2 rounded bg-red-50 p-2 text-xs text-red-800 dark:bg-red-950/40 dark:text-red-200">
                  {stage.error}
                </p>
              )}
              {stage && <StageDetail stageKey={s.key} detail={stage.detail ?? {}} />}
            </li>
          );
        })}
      </ol>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: unknown }) {
  if (value === undefined || value === null) return null;
  return (
    <span className="rounded bg-zinc-100 px-1.5 py-0.5 dark:bg-zinc-800">
      {label}: <b>{String(value)}</b>
    </span>
  );
}

function Warnings({ items }: { items: unknown }) {
  const list = Array.isArray(items) ? (items as string[]) : [];
  if (!list.length) return null;
  return (
    <details className="mt-1 text-[11px] text-amber-700 dark:text-amber-400">
      <summary className="cursor-pointer">{list.length} warning(s)</summary>
      <ul className="ml-4 list-disc">
        {list.map((w) => (
          <li key={w}>{w}</li>
        ))}
      </ul>
    </details>
  );
}

function StageDetail({ stageKey, detail }: { stageKey: string; detail: Record<string, unknown> }) {
  const d = detail;
  if (stageKey === "ingest")
    return (
      <div className="mt-2 flex flex-wrap gap-1.5 text-[11px]">
        <Stat label="pages" value={d.pages} />
        <Stat label="KB" value={typeof d.bytes === "number" ? Math.round(d.bytes / 1024) : null} />
        <Stat label="source" value={d.source_id} />
      </div>
    );
  if (stageKey === "parse")
    return (
      <div className="mt-2 text-[11px]">
        <div className="flex flex-wrap gap-1.5">
          <Stat label="blocks" value={d.blocks} />
          <Stat label="tables" value={d.tables} />
          <Stat label="references" value={d.references} />
        </div>
        <Warnings items={d.warnings} />
      </div>
    );
  if (stageKey === "structure")
    return (
      <div className="mt-2 text-[11px]">
        <div className="flex flex-wrap gap-1.5">
          <Stat label="sections" value={d.sections} />
          <Stat label="chunks" value={d.chunks} />
        </div>
        <Warnings items={d.warnings} />
      </div>
    );
  if (stageKey === "extract") {
    const groups = (Array.isArray(d.groups) ? d.groups : []) as GroupRun[];
    return (
      <div className="mt-2 space-y-2 text-[11px]">
        <div className="flex flex-wrap gap-1.5">
          <Stat label="items" value={d.items} />
          <Stat label="Gemini calls" value={d.llm_calls} />
        </div>
        {groups.length > 0 && (
          <table className="w-full text-left">
            <thead className="text-zinc-500">
              <tr>
                <th className="py-0.5 font-normal">group</th>
                <th className="font-normal">status</th>
                <th className="font-normal">model</th>
                <th className="text-right font-normal">time</th>
                <th className="text-right font-normal">items</th>
              </tr>
            </thead>
            <tbody>
              {groups.map((g) => (
                <tr key={g.name} className="border-t border-zinc-100 dark:border-zinc-800">
                  <td className="py-0.5">{g.name}</td>
                  <td>
                    {g.status}
                    {g.cached && " (cached)"}
                    {(g.attempts ?? 1) > 1 && " (retried)"}
                    {g.truncated && " (text cut)"}
                  </td>
                  <td className="text-zinc-500">{g.model ?? "–"}</td>
                  <td className="text-right">{g.seconds !== undefined ? fmt(g.seconds) : "–"}</td>
                  <td className="text-right">{g.items}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {groups
          .filter((g) => g.error)
          .map((g) => (
            <p key={g.name} className="text-red-700 dark:text-red-300">
              {g.name}: {g.error}
            </p>
          ))}
      </div>
    );
  }
  if (stageKey === "index")
    return (
      <div className="mt-2 text-[11px]">
        <div className="flex flex-wrap gap-1.5">
          <Stat label="passages" value={d.passages} />
          <Stat label="search" value={d.mode === "hybrid" ? "keyword + meaning" : "keyword only"} />
        </div>
        <Warnings items={d.warnings} />
      </div>
    );
  if (stageKey === "math")
    return (
      <div className="mt-2 text-[11px]">
        <div className="flex flex-wrap gap-1.5">
          <Stat label="equations" value={d.equations} />
          <Stat label="source" value={d.latex ? "LaTeX" : "PDF"} />
          <Stat label="symbols" value={d.symbols} />
          <Stat label="grounded" value={d.grounded} />
          <Stat label="Gemini calls" value={d.llm_calls} />
        </div>
        <Warnings items={d.warnings} />
      </div>
    );
  if (stageKey === "context")
    return (
      <div className="mt-2 text-[11px]">
        <div className="flex flex-wrap gap-1.5">
          <Stat label="source" value={d.source === "pdf" ? "PDF only" : "Semantic Scholar"} />
          <Stat label="references" value={d.references} />
          <Stat label="cited in text" value={d.cited_in_text} />
          <Stat label="citing papers" value={d.citations} />
          <Stat label="novelty relations" value={d.novelty_positions} />
          <Stat label="Gemini calls" value={d.llm_calls} />
        </div>
        <Warnings items={d.warnings} />
      </div>
    );
  if (stageKey === "code") {
    const comparisons = (d.comparisons ?? {}) as Record<string, number>;
    const repo = typeof d.repo === "string" ? d.repo.replace(/^https?:\/\//, "") : null;
    return (
      <div className="mt-2 text-[11px]">
        <div className="flex flex-wrap gap-1.5">
          <Stat label="status" value={d.status} />
          <Stat label="repo" value={repo} />
          <Stat label="files" value={d.files_scanned} />
          <Stat label="values" value={d.params_found} />
          {Object.entries(comparisons).map(([k, v]) => (
            <Stat key={k} label={k.replaceAll("_", " ")} value={v} />
          ))}
          <Stat label="sandbox" value={d.sandbox} />
        </div>
        <Warnings items={d.warnings} />
      </div>
    );
  }
  if (stageKey === "claims") {
    const verdicts = (d.verdicts ?? {}) as Record<string, number>;
    return (
      <div className="mt-2 text-[11px]">
        <div className="flex flex-wrap gap-1.5">
          <Stat label="claims" value={d.claims} />
          {Object.entries(verdicts).map(([k, v]) => (
            <Stat key={k} label={k.replace("_", " ")} value={v} />
          ))}
          <Stat label="results tables" value={d.tables} />
          <Stat label="Gemini calls" value={d.llm_calls} />
        </div>
        <Warnings items={d.warnings} />
      </div>
    );
  }
  if (stageKey === "repro") {
    const statuses = (d.statuses ?? {}) as Record<string, number>;
    const sources = (d.by_source ?? {}) as Record<string, number>;
    return (
      <div className="mt-2 text-[11px]">
        <div className="flex flex-wrap gap-1.5">
          <Stat label="score" value={typeof d.score === "number" ? Math.round(d.score) : null} />
          {Object.entries(statuses).map(([k, v]) => (
            <Stat key={k} label={k} value={v} />
          ))}
        </div>
        <div className="mt-1 flex flex-wrap gap-1.5">
          <Stat label="decided by rules" value={(sources.rule ?? 0) + (sources.extraction ?? 0)} />
          <Stat label="by GitHub" value={sources.repo} />
          <Stat label="by Gemini" value={sources.llm} />
          <Stat label="Gemini calls" value={d.llm_calls} />
        </div>
        <Warnings items={d.warnings} />
      </div>
    );
  }
  if (stageKey === "verify")
    return (
      <div className="mt-2 text-[11px]">
        <div className="flex flex-wrap gap-1.5">
          <Stat label="quotes found" value={d.located} />
          <Stat label="not found" value={d.unlocated} />
          <Stat label="support checked" value={d.support_checked} />
          <Stat
            label="grounding"
            value={
              typeof d.grounding_score === "number"
                ? `${Math.round(d.grounding_score * 100)}%`
                : null
            }
          />
          <Stat label="Gemini calls" value={d.llm_calls} />
        </div>
        <Warnings items={d.warnings} />
      </div>
    );
  return null;
}
