"use client";

import {
  ITEM_FIELDS,
  exportUrl,
  type Evidence,
  type ExportFormat,
  type ExtractionResponse,
  type GroundingStatus,
  type Item,
  type ItemField,
} from "@/lib/api";

// Same order and headings as the Markdown export (app/pipeline/export.py SECTIONS).
const FIELD_LABELS: Record<ItemField, string> = {
  problem: "Problem",
  task: "Task",
  contributions: "Contributions",
  method_summary: "Method",
  novelty: "Novelty",
  datasets: "Datasets",
  baselines: "Baselines",
  metrics: "Metrics",
  hyperparameters: "Hyperparameters",
  compute: "Compute",
  seeds_and_runs: "Seeds and runs",
  ablations: "Ablations",
  claims: "Claims",
  limitations: "Limitations",
  future_work: "Future work",
  ethics: "Ethics",
  code_urls: "Code",
};

export const GROUNDING_COLORS: Record<GroundingStatus, string> = {
  verified: "#059669",
  partial: "#d97706",
  unsupported: "#dc2626",
  unlocated: "#6b7280",
  unchecked: "#2563eb",
};

const GROUNDING_HELP: Record<GroundingStatus, string> = {
  verified: "quote found in the paper and it supports the value",
  partial: "quote found; it supports the value only in part",
  unsupported: "quote found, but it does not support the value",
  unlocated: "quote not found in the paper (possible hallucination)",
  unchecked: "quote found; support not checked yet",
};

export type EvidenceTarget = { itemId: string; index: number; evidence: Evidence };

export function Overview({
  paperId,
  extraction,
  activeKey,
  onEvidence,
}: {
  paperId: string;
  extraction: ExtractionResponse;
  activeKey: string | null;
  onEvidence: (target: EvidenceTarget) => void;
}) {
  const data = extraction.data;
  const meta = data.metadata;
  const facts = [meta.venue, meta.year, meta.arxiv_id && `arXiv:${meta.arxiv_id}`, meta.doi]
    .filter(Boolean)
    .join(" · ");

  return (
    <div className="space-y-5">
      <section className="space-y-2 rounded-lg border border-zinc-200 p-3 dark:border-zinc-800">
        <h2 className="font-semibold leading-snug">{meta.title ?? "Untitled paper"}</h2>
        {meta.authors.length > 0 && (
          <p className="text-xs text-zinc-600 dark:text-zinc-400">{meta.authors.join(", ")}</p>
        )}
        {facts && <p className="text-xs text-zinc-500">{facts}</p>}
        {meta.urls.length > 0 && (
          <p className="flex flex-wrap gap-2 text-xs">
            {meta.urls.map((u) => (
              <a
                key={u}
                href={u}
                target="_blank"
                rel="noreferrer"
                className="text-sky-700 underline dark:text-sky-400"
              >
                {u.replace(/^https?:\/\//, "")}
              </a>
            ))}
          </p>
        )}
        <GroundingSummary extraction={extraction} />
        <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
          <span className="text-zinc-500">Export:</span>
          {(["json", "md", "bib", "csv"] as ExportFormat[]).map((f) => (
            <a
              key={f}
              href={exportUrl(paperId, f)}
              className="rounded border border-zinc-300 px-2 py-0.5 uppercase hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-800"
            >
              {f}
            </a>
          ))}
        </div>
      </section>

      {ITEM_FIELDS.map((field) => {
        const items = data[field];
        return (
          <section key={field} className="space-y-1.5">
            <h3 className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
              {FIELD_LABELS[field]}
              <span className="ml-1 font-normal">({items.length})</span>
            </h3>
            {items.length === 0 ? (
              <p className="text-xs text-zinc-400">Not stated in the paper.</p>
            ) : (
              <ul className="space-y-2">
                {items.map((item) => (
                  <ItemRow
                    key={item.id}
                    field={field}
                    item={item}
                    activeKey={activeKey}
                    onEvidence={onEvidence}
                  />
                ))}
              </ul>
            )}
          </section>
        );
      })}
    </div>
  );
}

function GroundingSummary({ extraction }: { extraction: ExtractionResponse }) {
  const counts = extraction.status_counts;
  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs">
      <span className="text-zinc-500">
        Grounding:{" "}
        {extraction.verified && extraction.grounding_score !== null
          ? `${Math.round(extraction.grounding_score * 100)}% of items backed by a quote`
          : "not verified yet"}
      </span>
      {(Object.keys(GROUNDING_COLORS) as GroundingStatus[])
        .filter((s) => counts[s])
        .map((s) => (
          <span key={s} className="flex items-center gap-1" title={GROUNDING_HELP[s]}>
            <span
              className="inline-block h-2 w-2 rounded-full"
              style={{ background: GROUNDING_COLORS[s] }}
            />
            {s} {counts[s]}
          </span>
        ))}
    </div>
  );
}

function itemText(field: ItemField, item: Item) {
  if (field === "hyperparameters") {
    const scope = item.scope ? ` (${item.scope})` : "";
    return `${item.name}${scope}: ${item.value_raw || item.value}`;
  }
  if (field === "datasets") {
    const extra = [item.split, item.size].filter(Boolean).join(", ");
    return extra ? `${item.name} (${extra})` : item.name || item.value;
  }
  return item.value;
}

function ItemRow({
  field,
  item,
  activeKey,
  onEvidence,
}: {
  field: ItemField;
  item: Item;
  activeKey: string | null;
  onEvidence: (target: EvidenceTarget) => void;
}) {
  const text = itemText(field, item);
  return (
    <li className="space-y-1">
      <p className="leading-snug">
        {field === "code_urls" ? (
          <a
            href={text}
            target="_blank"
            rel="noreferrer"
            className="text-sky-700 underline dark:text-sky-400"
          >
            {text}
          </a>
        ) : (
          text
        )}
        {field === "hyperparameters" && item.value_norm != null && (
          <span className="ml-1 text-xs text-zinc-500">= {item.value_norm}</span>
        )}
        {item.source === "rule" && (
          <span className="ml-1 rounded bg-zinc-100 px-1 text-[10px] text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
            regex
          </span>
        )}
      </p>
      <div className="flex flex-wrap gap-1">
        {item.evidence.length === 0 ? (
          <span className="rounded-full border border-dashed border-zinc-400 px-2 py-0.5 text-[11px] text-zinc-500">
            unverified: no evidence
          </span>
        ) : (
          item.evidence.map((ev, i) => (
            <EvidenceChip
              key={i}
              evidence={ev}
              active={activeKey === `${item.id}#${i}`}
              onClick={() => onEvidence({ itemId: item.id, index: i, evidence: ev })}
            />
          ))
        )}
      </div>
    </li>
  );
}

export function EvidenceChip({
  evidence,
  active,
  onClick,
}: {
  evidence: Evidence;
  active: boolean;
  onClick: () => void;
}) {
  const color = GROUNDING_COLORS[evidence.grounding_status];
  return (
    <button
      type="button"
      onClick={onClick}
      data-status={evidence.grounding_status}
      title={`${GROUNDING_HELP[evidence.grounding_status]}\n\n“${evidence.quote}”`}
      className="evidence-chip flex max-w-full items-center gap-1 rounded-full border px-2 py-0.5 text-left text-[11px]"
      style={{
        borderColor: color,
        background: active ? `${color}30` : "transparent",
        fontWeight: active ? 600 : 400,
      }}
    >
      <span
        className="inline-block h-1.5 w-1.5 shrink-0 rounded-full"
        style={{ background: color }}
      />
      <span className="shrink-0">p. {evidence.page}</span>
      <span className="truncate text-zinc-600 dark:text-zinc-400">“{evidence.quote}”</span>
    </button>
  );
}
