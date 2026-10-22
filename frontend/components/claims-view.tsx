"use client";

import { useState } from "react";
import type { CheckedCell, ClaimCheck, ClaimsResponse, Verdict } from "@/lib/api";
import { EvidenceChip, type EvidenceTarget } from "./overview";

const VERDICTS: Record<Verdict, { label: string; color: string; help: string }> = {
  supported: {
    label: "Supported",
    color: "#059669",
    help: "the table cells give the claimed number (recomputed in Python)",
  },
  contradicted: {
    label: "Contradicted",
    color: "#dc2626",
    help: "the one cell that clearly matches the claim gives a different number",
  },
  unsupported: {
    label: "Unsupported",
    color: "#d97706",
    help: "tables with this metric exist, but no cell gives the claimed number",
  },
  weakly_supported: {
    label: "Weakly supported",
    color: "#2563eb",
    help: "no number to check; the paper's method is best in a results table",
  },
  unverifiable: {
    label: "Unverifiable",
    color: "#6b7280",
    help: "nothing to check against (no matching table, or no number)",
  },
};

const ORDER: Verdict[] = [
  "contradicted",
  "unsupported",
  "supported",
  "weakly_supported",
  "unverifiable",
];

export function ClaimsView({
  claims,
  activeKey,
  onEvidence,
  onShowTable,
}: {
  claims: ClaimsResponse;
  activeKey: string | null;
  onEvidence: (target: EvidenceTarget) => void;
  onShowTable: (tableId: string) => void;
}) {
  const report = claims.report;
  if (!report.claims.length)
    return <p className="text-zinc-500">The extraction found no claims to check.</p>;
  // Problems first: they are what a reader needs to look at.
  const sorted = [...report.claims].sort(
    (a, b) => ORDER.indexOf(a.verdict) - ORDER.indexOf(b.verdict),
  );
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs">
        {ORDER.filter((v) => report.counts[v]).map((v) => (
          <span key={v} className="flex items-center gap-1" title={VERDICTS[v].help}>
            <span
              className="inline-block h-2 w-2 rounded-full"
              style={{ background: VERDICTS[v].color }}
            />
            {VERDICTS[v].label} {report.counts[v]}
          </span>
        ))}
        <span className="text-zinc-400">
          numbers recomputed from the tables, tolerance ±{report.tolerance}
        </span>
      </div>
      <ul className="space-y-3">
        {sorted.map((c) => (
          <ClaimRow
            key={c.id}
            claim={c}
            activeKey={activeKey}
            onEvidence={onEvidence}
            onShowTable={onShowTable}
          />
        ))}
      </ul>
      {report.warnings.map((w) => (
        <p key={w} className="text-[11px] text-amber-700 dark:text-amber-400">
          ⚠ {w}
        </p>
      ))}
    </div>
  );
}

function ClaimRow({
  claim,
  activeKey,
  onEvidence,
  onShowTable,
}: {
  claim: ClaimCheck;
  activeKey: string | null;
  onEvidence: (target: EvidenceTarget) => void;
  onShowTable: (tableId: string) => void;
}) {
  const [open, setOpen] = useState(claim.verdict === "contradicted");
  const v = VERDICTS[claim.verdict];
  const fields = [
    claim.method && `method: ${claim.method}`,
    claim.baseline && `vs: ${claim.baseline}`,
    claim.metric && `metric: ${claim.metric}`,
    claim.dataset && `dataset: ${claim.dataset}`,
  ].filter(Boolean);
  return (
    <li
      className="space-y-1.5 rounded-lg border border-zinc-200 p-2.5 dark:border-zinc-800"
      data-verdict={claim.verdict}
    >
      <div className="flex items-start gap-2">
        <span
          className="mt-0.5 shrink-0 rounded px-1.5 py-0.5 text-[10px] font-medium text-white"
          style={{ background: v.color }}
          title={v.help}
        >
          {v.label}
        </span>
        <p className="leading-snug">{claim.text}</p>
      </div>
      <div className="flex flex-wrap gap-1">
        {claim.evidence.map((ev, i) => (
          <EvidenceChip
            key={i}
            evidence={ev}
            active={activeKey === `claim:${claim.id}#${i}`}
            onClick={() => onEvidence({ itemId: `claim:${claim.id}`, index: i, evidence: ev })}
          />
        ))}
      </div>
      <button onClick={() => setOpen(!open)} className="text-[11px] text-zinc-500 hover:underline">
        {open ? "▾" : "▸"} {claim.explanation || "details"}
      </button>
      {open && (
        <div className="space-y-1.5 pl-3 text-[11px]">
          {fields.length > 0 && (
            <p className="text-zinc-500">
              {claim.kind} · {fields.join(" · ")}
              {claim.comparator !== "exact" && ` · ${claim.comparator.replace("_", " ")}`}
            </p>
          )}
          <Numbers claim={claim} />
          {claim.checked_cells.length > 0 && (
            <table className="text-left">
              <tbody>
                {claim.checked_cells.map((cell, i) => (
                  <CellRow key={i} cell={cell} onShowTable={onShowTable} />
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </li>
  );
}

function Numbers({ claim }: { claim: ClaimCheck }) {
  const fmt = (x: number | null) => (x === null ? "–" : Number(x.toFixed(4)).toString());
  if (claim.kind === "score")
    return (
      <p>
        claimed <b>{fmt(claim.claimed_value)}</b> · table <b>{fmt(claim.table_value)}</b>
      </p>
    );
  if (claim.kind === "factor")
    return (
      <p>
        claimed <b>{fmt(claim.claimed_delta)}×</b> · recomputed{" "}
        <b>{fmt(claim.recomputed_factor)}×</b>
      </p>
    );
  if (claim.kind === "improvement")
    return (
      <p>
        claimed <b>{fmt(claim.claimed_delta)}</b>
        {claim.delta_unit === "percent" ? "%" : ""} · recomputed{" "}
        <b>{fmt(claim.recomputed_delta)}</b> absolute
        {claim.recomputed_relative !== null && (
          <>
            {" "}
            / <b>{fmt(claim.recomputed_relative)}%</b> relative
          </>
        )}
      </p>
    );
  return null;
}

function CellRow({
  cell,
  onShowTable,
}: {
  cell: CheckedCell;
  onShowTable: (tableId: string) => void;
}) {
  return (
    <tr>
      <td className="pr-2 text-zinc-500">{cell.role}</td>
      <td className="pr-2">
        <button onClick={() => onShowTable(cell.table_id)} className="hover:underline">
          {cell.table_label ?? "table"}
        </button>
      </td>
      <td className="pr-2">{cell.row_label}</td>
      <td className="pr-2 text-zinc-500">{cell.column}</td>
      <td className="font-semibold tabular-nums">{cell.text}</td>
    </tr>
  );
}
