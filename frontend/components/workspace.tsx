"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import dynamic from "next/dynamic";
import { useParams } from "next/navigation";
import { useMemo, useState } from "react";
import { getBlocks, getPaper, pdfUrl, rerunPaper, type Block, type PaperDetail } from "@/lib/api";
import { BLOCK_COLORS, BLOCK_TYPES, ROLE_LABELS } from "@/lib/blocks";
import { StatusBadge } from "./status-badge";
import { TableView } from "./table-view";

const PdfViewer = dynamic(() => import("./pdf/pdf-viewer"), {
  ssr: false,
  loading: () => <p className="p-4 text-sm text-zinc-500">Loading viewer…</p>,
});

const STAGES = ["ingest", "parse", "structure"] as const;
type Tab = "structure" | "tables" | "block";

export function Workspace() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [selected, setSelected] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("structure");
  const [visible, setVisible] = useState(
    () => new Set(BLOCK_TYPES.filter((t) => t !== "reference")),
  );

  const paper = useQuery({
    queryKey: ["paper", id],
    queryFn: () => getPaper(id),
    refetchInterval: (q) =>
      q.state.data && ["queued", "processing"].includes(q.state.data.status) ? 1500 : false,
  });
  const ready = paper.data?.status === "ready";
  const blocks = useQuery({
    queryKey: ["blocks", id, paper.data?.stages.structure?.finished_at],
    queryFn: () => getBlocks(id),
    enabled: ready,
  });
  const rerun = useMutation({
    mutationFn: () => rerunPaper(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["paper", id] }),
  });

  const byId = useMemo(
    () => new Map((blocks.data?.blocks ?? []).map((b) => [b.id, b])),
    [blocks.data],
  );
  const tables = (blocks.data?.blocks ?? []).filter((b) => b.type === "table");
  const select = (blockId: string) => {
    setSelected(blockId);
    setTab("block");
  };

  if (paper.isLoading) return <p className="p-6 text-sm text-zinc-500">Loading…</p>;
  if (paper.error || !paper.data)
    return (
      <p className="p-6 text-sm text-red-600">Could not load the paper: {paper.error?.message}</p>
    );
  const p = paper.data;

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <Header paper={p} onRerun={() => rerun.mutate()} rerunning={rerun.isPending} />
      {p.status === "failed" && (
        <p className="mx-6 mb-3 rounded-lg bg-red-50 p-3 text-sm text-red-800 dark:bg-red-950/40 dark:text-red-200">
          Processing failed: {p.error}
        </p>
      )}
      <div className="grid min-h-0 flex-1 grid-cols-1 border-t border-zinc-200 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)] dark:border-zinc-800">
        <div className="h-[70vh] min-h-0 lg:h-[calc(100vh-9.5rem)]">
          {blocks.data ? (
            <PdfViewer
              url={pdfUrl(id)}
              pages={blocks.data.pages}
              blocks={blocks.data.blocks}
              visibleTypes={visible}
              selectedId={selected}
              onSelect={select}
            />
          ) : (
            <p className="p-6 text-sm text-zinc-500">
              {ready ? "Loading blocks…" : "The PDF appears here once parsing finishes."}
            </p>
          )}
        </div>
        <aside className="flex min-h-0 flex-col border-l border-zinc-200 dark:border-zinc-800 lg:h-[calc(100vh-9.5rem)]">
          <Legend visible={visible} setVisible={setVisible} counts={p.parse?.block_counts ?? {}} />
          <nav className="flex gap-1 border-b border-zinc-200 px-3 dark:border-zinc-800">
            {(["structure", "tables", "block"] as Tab[]).map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`px-3 py-2 text-sm capitalize ${
                  tab === t
                    ? "border-b-2 border-zinc-900 font-medium dark:border-zinc-100"
                    : "text-zinc-500"
                }`}
              >
                {t === "tables" ? `Tables (${tables.length})` : t}
              </button>
            ))}
          </nav>
          <div className="min-h-0 flex-1 overflow-y-auto p-4 text-sm">
            {tab === "structure" && <Structure paper={p} byId={byId} onSelect={select} />}
            {tab === "tables" &&
              (tables.length ? (
                <div className="space-y-6">
                  {tables.map((t) => (
                    <div key={t.id} className="space-y-2">
                      <button
                        onClick={() => select(t.id)}
                        className="text-left font-medium hover:underline"
                      >
                        {t.text}
                      </button>
                      {t.table ? (
                        <TableView table={t.table} />
                      ) : (
                        <p className="text-zinc-500">No grid</p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-zinc-500">No tables detected.</p>
              ))}
            {tab === "block" && (
              <BlockInspector block={selected ? byId.get(selected) : undefined} />
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}

function Header({
  paper,
  onRerun,
  rerunning,
}: {
  paper: PaperDetail;
  onRerun: () => void;
  rerunning: boolean;
}) {
  const authors = paper.parse?.metadata.authors?.map((a) => a.name).join(", ");
  return (
    <header className="space-y-2 px-6 py-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h1 className="text-xl font-semibold tracking-tight">
            {paper.title ?? "Untitled paper"}
          </h1>
          {authors && <p className="text-sm text-zinc-500">{authors}</p>}
        </div>
        <button
          onClick={onRerun}
          disabled={rerunning || paper.status === "processing" || paper.status === "queued"}
          className="rounded-lg border border-zinc-300 px-3 py-1.5 text-xs disabled:opacity-40 dark:border-zinc-700"
        >
          Re-run parsing
        </button>
      </div>
      <div className="flex flex-wrap items-center gap-2 text-xs">
        {STAGES.map((s) => (
          <StatusBadge key={s} label={s} status={paper.stages[s]?.status ?? "queued"} />
        ))}
        {paper.parse && (
          <span className="text-zinc-500">
            parser: {paper.parse.parser} {paper.parse.parser_version} · {paper.page_count} pages ·{" "}
            {paper.parse.reference_count} references
          </span>
        )}
      </div>
      {paper.parse?.warnings.map((w) => (
        <p key={w} className="text-xs text-amber-700 dark:text-amber-400">
          ⚠ {w}
        </p>
      ))}
    </header>
  );
}

function Legend({
  visible,
  setVisible,
  counts,
}: {
  visible: Set<string>;
  setVisible: (s: Set<string>) => void;
  counts: Record<string, number>;
}) {
  return (
    <div className="flex flex-wrap gap-x-3 gap-y-1 border-b border-zinc-200 px-4 py-2 text-xs dark:border-zinc-800">
      <span className="text-zinc-500">Overlay:</span>
      {BLOCK_TYPES.filter((t) => counts[t]).map((t) => (
        <label key={t} className="flex cursor-pointer items-center gap-1">
          <input
            type="checkbox"
            checked={visible.has(t)}
            onChange={() => {
              const next = new Set(visible);
              if (next.has(t)) next.delete(t);
              else next.add(t);
              setVisible(next);
            }}
          />
          <span
            className="inline-block h-2.5 w-2.5 rounded-sm"
            style={{ background: BLOCK_COLORS[t] }}
          />
          {t} ({counts[t]})
        </label>
      ))}
    </div>
  );
}

function Structure({
  paper,
  byId,
  onSelect,
}: {
  paper: PaperDetail;
  byId: Map<string, Block>;
  onSelect: (id: string) => void;
}) {
  const sections = paper.parse?.sections ?? [];
  if (!sections.length)
    return (
      <p className="text-zinc-500">
        {paper.status === "ready" ? "No sections found." : "Waiting for parsing…"}
      </p>
    );
  return (
    <ul className="space-y-1">
      {sections.map((s) => {
        const first = s.block_ids.find((b) => byId.has(b));
        return (
          <li
            key={s.id}
            style={{ paddingLeft: (s.depth - 1) * 16 }}
            className="flex items-center justify-between gap-2"
          >
            <button
              onClick={() => first && onSelect(first)}
              className="truncate text-left hover:underline disabled:no-underline"
              disabled={!first}
            >
              {s.title}
            </button>
            <span
              className="shrink-0 rounded bg-zinc-100 px-1.5 py-0.5 text-[11px] text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300"
              title={`role from ${s.role_source}`}
            >
              {ROLE_LABELS[s.role] ?? s.role}
              {s.role_source === "llm" ? " · LLM" : ""}
            </span>
          </li>
        );
      })}
    </ul>
  );
}

function BlockInspector({ block }: { block: Block | undefined }) {
  if (!block) return <p className="text-zinc-500">Click a box on the PDF to inspect it.</p>;
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2 text-xs">
        <span
          className="rounded px-1.5 py-0.5 text-white"
          style={{ background: BLOCK_COLORS[block.type] }}
        >
          {block.type}
        </span>
        <span className="text-zinc-500">
          {block.id} · page {block.page}
          {block.role ? ` · ${ROLE_LABELS[block.role] ?? block.role}` : ""}
        </span>
      </div>
      {block.section_path.length > 0 && (
        <p className="text-xs text-zinc-500">{block.section_path.join(" › ")}</p>
      )}
      <p className="whitespace-pre-wrap leading-relaxed">{block.text}</p>
      {block.table && <TableView table={block.table} />}
    </div>
  );
}
