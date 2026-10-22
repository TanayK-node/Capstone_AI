"use client";

import { useState } from "react";
import type { CodeParam, CodeReport, Comparison } from "@/lib/api";
import { EvidenceChip, type EvidenceTarget } from "./overview";

const ROW: Record<Comparison["status"], { label: string; color: string }> = {
  mismatch: { label: "Mismatch", color: "#dc2626" },
  match: { label: "Match", color: "#059669" },
  only_in_paper: { label: "Not in code", color: "#d97706" },
  only_in_code: { label: "Not in paper", color: "#6b7280" },
};

const KIND: Record<string, string> = {
  argparse: "argparse default",
  flags: "flag default",
  click: "click default",
  default: "function default",
  constant: "constant",
  attr: "attribute",
  kwarg: "call argument",
  hparams: "hparams",
  config: "config file",
  readme: "README command",
};

const STATUS_TEXT: Record<CodeReport["status"], string> = {
  ok: "",
  no_repo: "No repository is linked in the paper, and none was found by search.",
  needs_confirmation: "The repository below is a guess. Confirm it or give the right one.",
  clone_failed: "The repository could not be cloned.",
  too_large: "The repository is too large to scan.",
  scan_failed: "The static scan failed.",
};

export function CodeView({
  report,
  activeKey,
  onEvidence,
  onConfirm,
  confirming,
}: {
  report: CodeReport;
  activeKey: string | null;
  onEvidence: (target: EvidenceTarget) => void;
  onConfirm: (url: string) => void;
  confirming: boolean;
}) {
  const [showCodeOnly, setShowCodeOnly] = useState(false);
  const order: Comparison["status"][] = ["mismatch", "only_in_paper", "match"];
  const rows = order.flatMap((s) => report.comparisons.filter((c) => c.status === s));
  const codeOnly = report.comparisons.filter((c) => c.status === "only_in_code");

  return (
    <div className="space-y-4">
      {report.status !== "ok" && (
        <div className="rounded-lg bg-amber-50 p-3 text-sm text-amber-900 dark:bg-amber-950/40 dark:text-amber-200">
          <p>{STATUS_TEXT[report.status]}</p>
          {report.warnings.map((w) => (
            <p key={w} className="mt-1 text-xs">
              {w}
            </p>
          ))}
        </div>
      )}
      <RepoCard report={report} />
      <ConfirmForm
        initial={report.candidates[0]?.url ?? ""}
        open={report.status !== "ok"}
        onConfirm={onConfirm}
        confirming={confirming}
      />

      {report.status === "ok" && (
        <>
          <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs">
            {(Object.keys(ROW) as Comparison["status"][])
              .filter((s) => report.counts[s])
              .map((s) => (
                <span key={s} className="flex items-center gap-1">
                  <span
                    className="inline-block h-2 w-2 rounded-full"
                    style={{ background: ROW[s].color }}
                  />
                  {ROW[s].label} {report.counts[s]}
                </span>
              ))}
            <span className="text-zinc-400">
              {report.files_scanned} files, {report.params_found} values scanned
            </span>
          </div>
          {rows.length === 0 ? (
            <p className="text-zinc-500">
              The paper states no hyperparameters that could be compared with the code.
            </p>
          ) : (
            <ul className="space-y-2.5">
              {rows.map((row, i) => (
                <ComparisonRow
                  key={`${row.canonical}-${i}`}
                  row={row}
                  rowKey={`code:${row.canonical}:${i}`}
                  activeKey={activeKey}
                  onEvidence={onEvidence}
                />
              ))}
            </ul>
          )}
          {codeOnly.length > 0 && (
            <div className="text-xs">
              <button
                onClick={() => setShowCodeOnly(!showCodeOnly)}
                className="text-zinc-500 hover:underline"
              >
                {showCodeOnly ? "▾" : "▸"} {codeOnly.length} hyperparameters set in the code but not
                stated in the paper
              </button>
              {showCodeOnly && (
                <ul className="mt-1 space-y-1 pl-3">
                  {codeOnly.map((row) => (
                    <li key={row.canonical}>
                      <b>{row.canonical}</b>: <Values values={row.code_values} />
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
          {report.warnings.length > 0 && (
            <div className="text-[11px] text-amber-700 dark:text-amber-400">
              {report.warnings.map((w) => (
                <p key={w}>⚠ {w}</p>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

function RepoCard({ report }: { report: CodeReport }) {
  const repo = report.repo;
  const top = report.candidates[0];
  if (!repo && !top) return null;
  return (
    <section className="space-y-1 rounded-lg border border-zinc-200 p-3 text-xs dark:border-zinc-800">
      {top && (
        <p>
          <a
            href={top.url}
            target="_blank"
            rel="noreferrer"
            className="font-medium text-sky-700 underline dark:text-sky-400"
          >
            {top.url.replace(/^https?:\/\//, "")}
          </a>{" "}
          <span className="text-zinc-500">
            · {top.source === "paper" ? "linked in the paper" : top.source.replace("_", " ")} ·
            confidence {Math.round(top.confidence * 100)}%
          </span>
        </p>
      )}
      {top && <p className="text-zinc-500">{top.reason}</p>}
      <p className="flex flex-wrap gap-x-3 text-zinc-600 dark:text-zinc-400">
        {repo?.license && <span>license: {repo.license}</span>}
        {repo?.stars != null && <span>★ {repo.stars}</span>}
        {repo?.pushed_at && <span>last push {repo.pushed_at.slice(0, 10)}</span>}
        {repo?.archived && <span>archived</span>}
        {report.reproduce_issues != null && (
          <span>{report.reproduce_issues} open issues about reproducing</span>
        )}
        {report.commit && <span>commit {report.commit.slice(0, 10)}</span>}
        {report.sandbox && (
          <span title="the repository is parsed, never executed">
            scanned in{" "}
            {report.sandbox === "docker" ? "the no-network sandbox" : "a separate process"}
          </span>
        )}
      </p>
      {report.candidates.length > 1 && (
        <p className="text-zinc-500">
          Other links in the paper:{" "}
          {report.candidates
            .slice(1)
            .map((c) => c.url.replace(/^https?:\/\/(www\.)?github\.com\//, ""))
            .join(", ")}
        </p>
      )}
    </section>
  );
}

function ConfirmForm({
  initial,
  open,
  onConfirm,
  confirming,
}: {
  initial: string;
  open: boolean;
  onConfirm: (url: string) => void;
  confirming: boolean;
}) {
  const [url, setUrl] = useState(initial);
  const [shown, setShown] = useState(open);
  if (!shown)
    return (
      <button onClick={() => setShown(true)} className="text-xs text-zinc-500 hover:underline">
        Wrong repository? Give the right one
      </button>
    );
  return (
    <form
      className="flex gap-2"
      onSubmit={(e) => {
        e.preventDefault();
        if (url.trim()) onConfirm(url.trim());
      }}
    >
      <input
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="https://github.com/owner/repo"
        className="min-w-0 flex-1 rounded border border-zinc-300 bg-transparent px-2 py-1 text-xs dark:border-zinc-700"
      />
      <button
        type="submit"
        disabled={confirming || !url.trim()}
        className="rounded bg-zinc-900 px-3 py-1 text-xs text-white disabled:opacity-40 dark:bg-zinc-100 dark:text-zinc-900"
      >
        {confirming ? "Checking…" : "Use this repository"}
      </button>
    </form>
  );
}

function ComparisonRow({
  row,
  rowKey,
  activeKey,
  onEvidence,
}: {
  row: Comparison;
  rowKey: string;
  activeKey: string | null;
  onEvidence: (target: EvidenceTarget) => void;
}) {
  const st = ROW[row.status];
  return (
    <li className="space-y-1" data-status={row.status}>
      <div className="flex items-start gap-2">
        <span
          className="mt-0.5 w-20 shrink-0 rounded px-1.5 py-0.5 text-center text-[10px] font-medium text-white"
          style={{ background: st.color }}
        >
          {st.label}
        </span>
        <div className="min-w-0 flex-1 text-xs">
          <p>
            <b>{row.paper_name || row.canonical}</b>
            {row.paper_scope && <span className="text-zinc-500"> ({row.paper_scope})</span>}: paper{" "}
            <b>{row.paper_value}</b>
          </p>
          <p className="text-zinc-600 dark:text-zinc-400">
            code: <Values values={row.code_values} />
          </p>
          {row.note && <p className="text-zinc-500">{row.note}</p>}
        </div>
      </div>
      {row.paper_evidence.length > 0 && (
        <div className="ml-[5.5rem] flex flex-wrap gap-1">
          {row.paper_evidence.map((ev, i) => (
            <EvidenceChip
              key={i}
              evidence={ev}
              active={activeKey === `${rowKey}#${i}`}
              onClick={() => onEvidence({ itemId: rowKey, index: i, evidence: ev })}
            />
          ))}
        </div>
      )}
    </li>
  );
}

function Values({ values }: { values: CodeParam[] }) {
  if (!values.length) return <span className="italic">not found</span>;
  return (
    <>
      {values.map((p, i) => (
        <span key={i}>
          {i > 0 && ", "}
          <b className="tabular-nums">{p.value}</b>{" "}
          <span className="text-zinc-400" title={p.name}>
            [{p.file}
            {p.line ? `:${p.line}` : ""} · {KIND[p.kind] ?? p.kind}]
          </span>
        </span>
      ))}
    </>
  );
}
