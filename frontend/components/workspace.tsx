"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import dynamic from "next/dynamic";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import {
  eventsUrl,
  getBlocks,
  getClaims,
  getCode,
  confirmRepo,
  getExtraction,
  getGlossary,
  getPaper,
  getReproducibility,
  getTables,
  pdfUrl,
  rerunPaper,
  type Block,
  type PaperDetail,
} from "@/lib/api";
import { BLOCK_COLORS, BLOCK_TYPES, ROLE_LABELS } from "@/lib/blocks";
import { GROUNDING_COLORS, Overview, type EvidenceTarget } from "./overview";
import { PipelineView } from "./pipeline-view";
import { ChatView } from "./chat-view";
import { ClaimsView } from "./claims-view";
import { CodeView } from "./code-view";
import { MathView } from "./math-view";
import { ReproView } from "./repro-view";
import { ResultsView } from "./results-view";
import type { Highlight } from "./pdf/pdf-viewer";
import { StatusBadge } from "./status-badge";
import { TableView } from "./table-view";

const PdfViewer = dynamic(() => import("./pdf/pdf-viewer"), {
  ssr: false,
  loading: () => <p className="p-4 text-sm text-zinc-500">Loading viewer…</p>,
});

const STAGES = [
  "ingest",
  "parse",
  "structure",
  "index",
  "extract",
  "verify",
  "repro",
  "claims",
  "code",
  "math",
] as const;
const ACTIVE = ["queued", "processing"];
const TABS = [
  "pipeline",
  "overview",
  "chat",
  "reproducibility",
  "claims",
  "code",
  "math",
  "results",
  "structure",
  "block",
] as const;
type Tab = (typeof TABS)[number];

export function Workspace() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [selected, setSelected] = useState<string | null>(null);
  // null = not picked yet: follow the paper (Pipeline while it runs, Overview once done).
  const [pickedTab, setTab] = useState<Tab | null>(null);
  // The block overlay is a debug view; evidence highlights are drawn on their own layer.
  const [showBlocks, setShowBlocks] = useState(false);
  const [visible, setVisible] = useState(
    () => new Set(BLOCK_TYPES.filter((t) => t !== "reference")),
  );
  const [evidence, setEvidence] = useState<EvidenceTarget | null>(null);

  const paper = useQuery({
    queryKey: ["paper", id],
    queryFn: () => getPaper(id),
    // Server-sent events drive updates (below); this slow poll is only a safety net.
    refetchInterval: (q) => (q.state.data && ACTIVE.includes(q.state.data.status) ? 5000 : false),
  });
  const status = paper.data?.status;
  const tab: Tab = pickedTab ?? (status && ACTIVE.includes(status) ? "pipeline" : "overview");
  const stages = paper.data?.stages;
  const structured = stages?.structure?.status === "done";
  const extracted = stages?.extract?.status === "done";
  const blocks = useQuery({
    queryKey: ["blocks", id, stages?.structure?.finished_at],
    queryFn: () => getBlocks(id),
    enabled: structured,
  });
  const extraction = useQuery({
    queryKey: ["extraction", id, stages?.extract?.finished_at, stages?.verify?.finished_at],
    queryFn: () => getExtraction(id),
    enabled: extracted,
  });
  const repro = useQuery({
    queryKey: ["repro", id, stages?.repro?.finished_at],
    queryFn: () => getReproducibility(id),
    enabled: stages?.repro?.status === "done",
  });
  const claims = useQuery({
    queryKey: ["claims", id, stages?.claims?.finished_at],
    queryFn: () => getClaims(id),
    enabled: stages?.claims?.status === "done",
  });
  const code = useQuery({
    queryKey: ["code", id, stages?.code?.finished_at],
    queryFn: () => getCode(id),
    enabled: stages?.code?.status === "done",
  });
  const glossary = useQuery({
    queryKey: ["glossary", id, stages?.math?.finished_at],
    queryFn: () => getGlossary(id),
    enabled: stages?.math?.status === "done",
  });
  const confirm = useMutation({
    mutationFn: (url: string) => confirmRepo(id, url),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["paper", id] }),
  });
  // Rebuilt from the parse; the extraction (when there is one) names the paper's method.
  const results = useQuery({
    queryKey: ["tables", id, stages?.structure?.finished_at, stages?.extract?.finished_at],
    queryFn: () => getTables(id),
    enabled: structured,
  });
  const rerun = useMutation({
    mutationFn: (only?: string[]) => rerunPaper(id, only),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["paper", id] }),
  });

  // Live progress: refetch the paper whenever a stage changes, until a final status.
  const active = status !== undefined && ACTIVE.includes(status);
  useEffect(() => {
    if (!active) return;
    const source = new EventSource(eventsUrl(id));
    const refresh = () => queryClient.invalidateQueries({ queryKey: ["paper", id] });
    source.addEventListener("stage", refresh);
    source.addEventListener("status", refresh);
    source.addEventListener("done", () => {
      refresh();
      source.close();
    });
    return () => source.close();
  }, [active, id, queryClient]);

  const byId = useMemo(
    () => new Map((blocks.data?.blocks ?? []).map((b) => [b.id, b])),
    [blocks.data],
  );
  const select = (blockId: string) => {
    setSelected(blockId);
    setTab("block");
  };

  // Show a whole table in the PDF (Results tab): highlighted like evidence, block boxes.
  const showTable = (tableId: string) => {
    const block = byId.get(tableId);
    setEvidence({
      itemId: `table:${tableId}`,
      index: 0,
      evidence: {
        chunk_id: tableId,
        page: block?.page ?? 1,
        bbox: null,
        boxes: [],
        quote: block?.text ?? "",
        grounding_status: "verified",
        match_score: null,
      },
    });
  };

  // Evidence located in the paper has its own sentence boxes. An unlocated quote has none,
  // so the cited paragraph is shown instead, in the "unlocated" grey.
  const highlight = useMemo<Highlight | null>(() => {
    if (!evidence) return null;
    const ev = evidence.evidence;
    const fallback = byId.get(ev.chunk_id);
    const boxes = ev.boxes.length ? ev.boxes : (fallback?.boxes ?? []);
    if (!boxes.length) return null;
    return {
      key: `${evidence.itemId}#${evidence.index}`,
      boxes,
      color: GROUNDING_COLORS[ev.grounding_status],
    };
  }, [evidence, byId]);

  if (paper.isLoading) return <p className="p-6 text-sm text-zinc-500">Loading…</p>;
  if (paper.error || !paper.data)
    return (
      <p className="p-6 text-sm text-red-600">Could not load the paper: {paper.error?.message}</p>
    );
  const p = paper.data;

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <Header paper={p} onRerun={(only) => rerun.mutate(only)} rerunning={rerun.isPending} />
      {p.status === "failed" && (
        <p className="mx-6 mb-3 rounded-lg bg-red-50 p-3 text-sm text-red-800 dark:bg-red-950/40 dark:text-red-200">
          Processing failed: {p.error}
        </p>
      )}
      {p.status === "partial" && (
        <p className="mx-6 mb-3 rounded-lg bg-amber-50 p-3 text-sm text-amber-900 dark:bg-amber-950/40 dark:text-amber-200">
          The paper was parsed, but analysis did not finish: {p.error}
        </p>
      )}
      <div className="grid min-h-0 flex-1 grid-cols-1 border-t border-zinc-200 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)] dark:border-zinc-800">
        <div className="h-[70vh] min-h-0 lg:h-[calc(100vh-9.5rem)]">
          {blocks.data ? (
            <PdfViewer
              url={pdfUrl(id)}
              pages={blocks.data.pages}
              blocks={blocks.data.blocks}
              visibleTypes={showBlocks ? visible : new Set()}
              selectedId={showBlocks || tab === "block" ? selected : null}
              onSelect={select}
              highlight={highlight}
            />
          ) : (
            <p className="p-6 text-sm text-zinc-500">
              {structured ? "Loading blocks…" : "The PDF appears here once parsing finishes."}
            </p>
          )}
        </div>
        <aside className="flex min-h-0 flex-col border-l border-zinc-200 dark:border-zinc-800 lg:h-[calc(100vh-9.5rem)]">
          <Legend
            show={showBlocks}
            setShow={setShowBlocks}
            visible={visible}
            setVisible={setVisible}
            counts={p.parse?.block_counts ?? {}}
          />
          <nav className="flex gap-1 overflow-x-auto whitespace-nowrap border-b border-zinc-200 px-3 dark:border-zinc-800">
            {TABS.map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`px-3 py-2 text-sm capitalize ${
                  tab === t
                    ? "border-b-2 border-zinc-900 font-medium dark:border-zinc-100"
                    : "text-zinc-500"
                }`}
              >
                {t === "results" && results.data ? `Results (${results.data.length})` : t}
              </button>
            ))}
          </nav>
          <div className="min-h-0 flex-1 overflow-y-auto p-4 text-sm">
            {tab === "pipeline" && <PipelineView paper={p} />}
            {tab === "overview" &&
              (extraction.data ? (
                <Overview
                  paperId={id}
                  extraction={extraction.data}
                  activeKey={highlight?.key ?? null}
                  onEvidence={setEvidence}
                />
              ) : (
                <p className="text-zinc-500">
                  {extraction.error
                    ? `Could not load the extraction: ${extraction.error.message}`
                    : stages?.extract?.status === "failed"
                      ? "Extraction failed (see above). Re-run the analysis once it is fixed."
                      : ACTIVE.includes(p.status)
                        ? "Extracting… the overview appears here when it is done."
                        : "No extraction yet."}
                </p>
              ))}
            {tab === "reproducibility" &&
              (repro.data ? (
                <ReproView
                  repro={repro.data}
                  activeKey={highlight?.key ?? null}
                  onEvidence={setEvidence}
                />
              ) : (
                <p className="text-zinc-500">
                  {repro.error
                    ? `Could not load the scorecard: ${repro.error.message}`
                    : stages?.repro?.status === "failed"
                      ? "The reproducibility check failed (see the Pipeline tab)."
                      : ACTIVE.includes(p.status)
                        ? "Scoring… the scorecard appears here when it is done."
                        : "No scorecard yet. Re-run the analysis to create one."}
                </p>
              ))}
            {tab === "structure" && <Structure paper={p} byId={byId} onSelect={select} />}
            {tab === "claims" &&
              (claims.data ? (
                <ClaimsView
                  claims={claims.data}
                  activeKey={highlight?.key ?? null}
                  onEvidence={setEvidence}
                  onShowTable={showTable}
                />
              ) : (
                <p className="text-zinc-500">
                  {claims.error
                    ? `Could not load the claims: ${claims.error.message}`
                    : stages?.claims?.status === "failed"
                      ? "Claim checking failed (see the Pipeline tab)."
                      : ACTIVE.includes(p.status)
                        ? "Checking claims… they appear here when done."
                        : "No claim report yet. Re-run the analysis to create one."}
                </p>
              ))}
            {tab === "chat" &&
              (structured ? (
                <ChatView
                  paperId={id}
                  activeKey={highlight?.key ?? null}
                  onEvidence={setEvidence}
                />
              ) : (
                <p className="text-zinc-500">Chat opens once the paper is parsed.</p>
              ))}
            {tab === "code" &&
              (code.data ? (
                <CodeView
                  report={code.data.report}
                  activeKey={highlight?.key ?? null}
                  onEvidence={setEvidence}
                  onConfirm={(url) => confirm.mutate(url)}
                  confirming={confirm.isPending}
                />
              ) : (
                <p className="text-zinc-500">
                  {code.error
                    ? `Could not load the code report: ${code.error.message}`
                    : stages?.code?.status === "failed"
                      ? "The code check failed (see the Pipeline tab)."
                      : ACTIVE.includes(p.status)
                        ? "Checking the code… the comparison appears here when done."
                        : "No code report yet. Re-run the analysis to create one."}
                </p>
              ))}
            {confirm.isError && tab === "code" && (
              <p className="mt-2 text-xs text-red-600">{confirm.error.message}</p>
            )}
            {tab === "math" &&
              (glossary.data ? (
                <MathView
                  report={glossary.data.report}
                  activeKey={highlight?.key ?? null}
                  onEvidence={setEvidence}
                />
              ) : (
                <p className="text-zinc-500">
                  {glossary.error
                    ? `Could not load the glossary: ${glossary.error.message}`
                    : stages?.math?.status === "failed"
                      ? "The math stage failed (see the Pipeline tab)."
                      : ACTIVE.includes(p.status)
                        ? "Reading equations… they appear here when done."
                        : "No glossary yet. Re-run the analysis to create one."}
                </p>
              ))}
            {tab === "results" &&
              (results.data ? (
                <ResultsView paperId={id} tables={results.data} onShowTable={showTable} />
              ) : (
                <p className="text-zinc-500">
                  {results.error
                    ? `Could not load the tables: ${results.error.message}`
                    : structured
                      ? "Loading tables…"
                      : "Tables appear here once parsing finishes."}
                </p>
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
  onRerun: (stages?: string[]) => void;
  rerunning: boolean;
}) {
  const busy = rerunning || ACTIVE.includes(paper.status);
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
        <div className="flex gap-2">
          {paper.stages.structure?.status === "done" && (
            <button
              onClick={() =>
                onRerun(["index", "extract", "verify", "repro", "claims", "code", "math"])
              }
              disabled={busy}
              className="rounded-lg border border-zinc-300 px-3 py-1.5 text-xs disabled:opacity-40 dark:border-zinc-700"
            >
              Re-run analysis
            </button>
          )}
          <button
            onClick={() => onRerun()}
            disabled={busy}
            className="rounded-lg border border-zinc-300 px-3 py-1.5 text-xs disabled:opacity-40 dark:border-zinc-700"
          >
            Re-run all
          </button>
        </div>
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
  show,
  setShow,
  visible,
  setVisible,
  counts,
}: {
  show: boolean;
  setShow: (v: boolean) => void;
  visible: Set<string>;
  setVisible: (s: Set<string>) => void;
  counts: Record<string, number>;
}) {
  return (
    <div className="flex flex-wrap gap-x-3 gap-y-1 border-b border-zinc-200 px-4 py-2 text-xs dark:border-zinc-800">
      <label className="flex cursor-pointer items-center gap-1 text-zinc-500">
        <input type="checkbox" checked={show} onChange={() => setShow(!show)} />
        Block overlay (debug)
      </label>
      {show &&
        BLOCK_TYPES.filter((t) => counts[t]).map((t) => (
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
        {paper.stages.structure?.status === "done" ? "No sections found." : "Waiting for parsing…"}
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
