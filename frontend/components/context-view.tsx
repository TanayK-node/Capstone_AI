"use client";

import { useState } from "react";
import type { ContextReport, GraphNode, Relation } from "@/lib/api";
import { EvidenceChip, type EvidenceTarget } from "./overview";

const W = 640;
const H = 400;
const CX = W / 2;
const CY = H / 2;
const COLORS = { paper: "#18181b", reference: "#2563eb", citation: "#059669" };
const RELATIONS: Record<Relation, string> = {
  extends: "extends",
  uses: "uses",
  compares_to: "compares to",
  differs_from: "differs from",
};

/** Node size: Semantic Scholar's citation count when known, else in-text mentions. */
function radius(n: GraphNode): number {
  if (n.citation_count != null) return 4 + Math.min(10, 1.6 * Math.log10(n.citation_count + 1));
  return 4 + Math.min(8, 1.5 * n.mentions);
}

/** Spread nodes on an arc: references on the left, citing papers on the right. */
function arc(nodes: GraphNode[], side: "left" | "right") {
  const span = Math.PI * 0.85;
  return nodes.map((n, i) => {
    const t = nodes.length === 1 ? 0.5 : i / (nodes.length - 1);
    const angle = -span / 2 + t * span; // top to bottom
    const dir = side === "left" ? -1 : 1;
    // alternate two rings so neighbouring nodes do not overlap
    const ring = i % 2 === 0 ? 1 : 0.8;
    return {
      node: n,
      x: CX + dir * Math.cos(angle) * (W / 2 - 40) * ring,
      y: CY + Math.sin(angle) * (H / 2 - 30) * ring,
    };
  });
}

function short(title: string, max = 28) {
  return title.length > max ? `${title.slice(0, max - 1)}…` : title;
}

function fmtCount(n: number | null) {
  if (n == null) return "–";
  return n >= 1000 ? `${(n / 1000).toFixed(n >= 10000 ? 0 : 1)}k` : String(n);
}

/** Citation graph and novelty positioning (M12). The graph is laid out in plain SVG:
 * the paper in the middle, its key references on the left, papers citing it on the right. */
export function ContextView({
  report,
  activeKey,
  onEvidence,
}: {
  report: ContextReport;
  activeKey: string | null;
  onEvidence: (target: EvidenceTarget) => void;
}) {
  const [selected, setSelected] = useState<string | null>(null);
  const [hover, setHover] = useState<string | null>(null);
  const placed = [...arc(report.references, "left"), ...arc(report.citations, "right")];
  const all = [report.paper, ...report.references, ...report.citations];
  const current = all.find((n) => n.id === selected) ?? null;
  const hovered = placed.find((p) => p.node.id === hover);

  return (
    <div className="space-y-5">
      <p className="text-xs text-zinc-500">
        {report.source === "semantic_scholar"
          ? `${report.reference_count} references · cited by ${fmtCount(report.citation_count)} (${fmtCount(report.influential_citation_count)} influential), from Semantic Scholar.`
          : `${report.reference_count} references from the PDF; Semantic Scholar was not available, so there are no citing papers.`}{" "}
        Left: the references this paper cites most. Right: influential and most-cited papers citing
        it.
      </p>
      {report.warnings.map((w) => (
        <p key={w} className="text-xs text-amber-700 dark:text-amber-400">
          ⚠ {w}
        </p>
      ))}

      <figure className="relative rounded-lg border border-zinc-200 dark:border-zinc-800">
        <svg
          viewBox={`0 0 ${W} ${H}`}
          className="h-auto w-full"
          role="img"
          aria-label="Citation graph"
          data-graph
        >
          {placed.map(({ node, x, y }) => (
            <line
              key={`e-${node.id}`}
              x1={x}
              y1={y}
              x2={CX}
              y2={CY}
              stroke={COLORS[node.kind]}
              strokeOpacity={selected === node.id || hover === node.id ? 0.8 : 0.18}
              strokeWidth={node.kind === "reference" ? 1 + Math.min(3, node.mentions * 0.5) : 1}
            />
          ))}
          {placed.map(({ node, x, y }) => (
            <g
              key={node.id}
              transform={`translate(${x},${y})`}
              className="cursor-pointer"
              onClick={() => setSelected(selected === node.id ? null : node.id)}
              onMouseEnter={() => setHover(node.id)}
              onMouseLeave={() => setHover(null)}
            >
              <circle
                r={radius(node)}
                fill={COLORS[node.kind]}
                fillOpacity={selected === node.id ? 1 : 0.75}
                stroke={node.influential ? "#f59e0b" : "white"}
                strokeWidth={node.influential ? 2.5 : 1}
              />
              <title>{node.title}</title>
            </g>
          ))}
          <g className="cursor-pointer" onClick={() => setSelected("paper")}>
            <circle cx={CX} cy={CY} r={16} fill={COLORS.paper} />
            <text
              x={CX}
              y={CY + 32}
              textAnchor="middle"
              className="fill-zinc-700 text-[11px] font-medium dark:fill-zinc-200"
            >
              {short(report.paper.title, 40)}
            </text>
          </g>
          {hovered && (
            <text
              x={hovered.x < CX ? hovered.x + 10 : hovered.x - 10}
              y={hovered.y + 4}
              textAnchor={hovered.x < CX ? "start" : "end"}
              className="pointer-events-none fill-zinc-900 text-[11px] dark:fill-zinc-100"
              stroke="white"
              strokeWidth={3}
              paintOrder="stroke"
            >
              {short(hovered.node.title, 44)}
              {hovered.node.year ? ` (${hovered.node.year})` : ""}
            </text>
          )}
        </svg>
        <figcaption className="flex flex-wrap gap-3 border-t border-zinc-200 px-3 py-1.5 text-[11px] text-zinc-500 dark:border-zinc-800">
          <Key
            color={COLORS.reference}
            label="reference (size: citations, line: in-text mentions)"
          />
          <Key color={COLORS.citation} label="citing paper" />
          <span className="flex items-center gap-1">
            <span className="inline-block h-2.5 w-2.5 rounded-full border-2 border-amber-500" />
            influential (Semantic Scholar)
          </span>
        </figcaption>
      </figure>

      {current && (
        <NodeDetail
          node={current}
          activeKey={activeKey}
          onEvidence={onEvidence}
          onClose={() => setSelected(null)}
        />
      )}

      {report.novelty && (
        <section className="space-y-2">
          <h3 className="font-medium">Novelty positioning</h3>
          <p className="leading-relaxed">{report.novelty.summary}</p>
          <p className="text-[11px] text-zinc-500">
            Written by Gemini from the abstracts of the references the paper cites most; each
            relation below quotes the paper.
          </p>
          <ul className="space-y-2">
            {report.novelty.positions.map((p, i) => (
              <li
                key={i}
                className="space-y-1 rounded border border-zinc-200 p-2 dark:border-zinc-800"
              >
                <div className="flex flex-wrap items-baseline gap-2">
                  <span className="rounded bg-zinc-100 px-1.5 py-0.5 text-[11px] dark:bg-zinc-800">
                    {RELATIONS[p.relation]}
                  </span>
                  <button
                    type="button"
                    onClick={() => setSelected(p.node)}
                    className="text-left font-medium hover:underline"
                  >
                    {short(p.title, 70)}
                  </button>
                </div>
                <p>{p.statement}</p>
                <div className="flex flex-wrap gap-1.5">
                  {p.evidence.map((ev, j) => (
                    <EvidenceChip
                      key={j}
                      evidence={ev}
                      active={activeKey === `nov:${i}#${j}`}
                      onClick={() => onEvidence({ itemId: `nov:${i}`, index: j, evidence: ev })}
                    />
                  ))}
                  {p.evidence.length === 0 && (
                    <span className="text-[11px] text-zinc-500">no quote: unverified</span>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </section>
      )}

      <NodeList
        title="Key references"
        nodes={report.references}
        selected={selected}
        onSelect={setSelected}
        extra={(n) => (n.mentions ? `cited ${n.mentions}× in the text` : "not cited in the text")}
      />
      {report.citations.length > 0 && (
        <NodeList
          title="Cited by"
          nodes={report.citations}
          selected={selected}
          onSelect={setSelected}
          extra={(n) => `${fmtCount(n.citation_count)} citations`}
        />
      )}
    </div>
  );
}

function Key({ color, label }: { color: string; label: string }) {
  return (
    <span className="flex items-center gap-1">
      <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: color }} />
      {label}
    </span>
  );
}

function NodeDetail({
  node,
  activeKey,
  onEvidence,
  onClose,
}: {
  node: GraphNode;
  activeKey: string | null;
  onEvidence: (target: EvidenceTarget) => void;
  onClose: () => void;
}) {
  return (
    <section
      className="space-y-1.5 rounded-lg border border-zinc-300 p-3 dark:border-zinc-700"
      data-node
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-medium">{node.title}</h3>
        <button
          type="button"
          onClick={onClose}
          className="text-xs text-zinc-500"
          aria-label="Close"
        >
          ✕
        </button>
      </div>
      <p className="text-xs text-zinc-500">
        {[node.authors.join(", "), node.venue, node.year].filter(Boolean).join(" · ") || "–"}
      </p>
      <p className="text-xs">
        {node.kind === "reference" &&
          (node.mentions ? `Cited ${node.mentions}× in this paper. ` : "Not cited in the text. ")}
        {node.citation_count != null && `${fmtCount(node.citation_count)} citations overall. `}
        {node.influential && "Influential (Semantic Scholar). "}
        {node.url && (
          <a href={node.url} target="_blank" rel="noreferrer" className="underline">
            Open
          </a>
        )}
      </p>
      {node.evidence.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {node.evidence.map((ev, i) => (
            <EvidenceChip
              key={i}
              evidence={ev}
              active={activeKey === `node:${node.id}#${i}`}
              onClick={() => onEvidence({ itemId: `node:${node.id}`, index: i, evidence: ev })}
            />
          ))}
        </div>
      )}
    </section>
  );
}

function NodeList({
  title,
  nodes,
  selected,
  onSelect,
  extra,
}: {
  title: string;
  nodes: GraphNode[];
  selected: string | null;
  onSelect: (id: string) => void;
  extra: (n: GraphNode) => string;
}) {
  return (
    <section className="space-y-1">
      <h3 className="font-medium">
        {title} ({nodes.length})
      </h3>
      <ol className="space-y-0.5">
        {nodes.map((n) => (
          <li key={n.id}>
            <button
              type="button"
              onClick={() => onSelect(n.id)}
              className={`flex w-full items-baseline gap-2 rounded px-1.5 py-1 text-left hover:bg-zinc-100 dark:hover:bg-zinc-800 ${
                selected === n.id ? "bg-zinc-100 dark:bg-zinc-800" : ""
              }`}
            >
              <span
                className="inline-block h-2 w-2 shrink-0 rounded-full"
                style={{
                  background: COLORS[n.kind],
                  outline: n.influential ? "2px solid #f59e0b" : undefined,
                }}
              />
              <span className="min-w-0 flex-1 truncate">{n.title}</span>
              <span className="shrink-0 text-[11px] text-zinc-500">
                {n.year ?? ""} · {extra(n)}
              </span>
            </button>
          </li>
        ))}
      </ol>
    </section>
  );
}
