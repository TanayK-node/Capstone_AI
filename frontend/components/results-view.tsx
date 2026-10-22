"use client";

import { useState } from "react";
import { tablesCsvUrl, type ResultsTable } from "@/lib/api";

/**
 * Results tables (M9): typed values, best value per column (green), the paper's own rows
 * (tinted). Cells are editable to fix parsing mistakes; edits stay in the browser and go
 * into "Download edited CSV" only (the stored parse is never changed from here).
 */
export function ResultsView({
  paperId,
  tables,
  onShowTable,
}: {
  paperId: string;
  tables: ResultsTable[];
  onShowTable: (tableId: string) => void;
}) {
  if (!tables.length)
    return <p className="text-zinc-500">No results tables with numbers were found.</p>;
  return (
    <div className="space-y-6">
      <p className="flex flex-wrap items-center gap-2 text-xs text-zinc-500">
        <span>
          {tables.length} results table{tables.length > 1 ? "s" : ""}. Best value per column in
          green; the paper&apos;s own method tinted; click a cell to correct it.
        </span>
        <a
          href={tablesCsvUrl(paperId)}
          className="rounded border border-zinc-300 px-2 py-0.5 hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-800"
        >
          All tables (CSV)
        </a>
      </p>
      {tables.map((t) => (
        <EditableTable key={t.table_id} table={t} onShow={() => onShowTable(t.table_id)} />
      ))}
    </div>
  );
}

function EditableTable({ table, onShow }: { table: ResultsTable; onShow: () => void }) {
  const numeric = table.columns.filter((c) => c.numeric);
  // Edited cell texts, keyed "row:col"; only differences from the parse are stored.
  const [edits, setEdits] = useState<Record<string, string>>({});
  const text = (row: number, col: number, original: string) => edits[`${row}:${col}`] ?? original;

  const download = () => {
    const lines = [["method", ...numeric.map((c) => c.header || c.group)]];
    for (const r of table.rows) {
      const byCol = new Map(r.cells.map((c) => [c.col, c.text]));
      lines.push([
        text(r.index, -1, r.label),
        ...numeric.map((c) => text(r.index, c.index, byCol.get(c.index) ?? "")),
      ]);
    }
    const csv = lines
      .map((l) => l.map((v) => (/[",\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v)).join(","))
      .join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = `${(table.label ?? table.table_id).replace(/\s+/g, "_")}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };
  const edited = Object.keys(edits).length;

  return (
    <section className="space-y-2" data-table={table.table_id}>
      <div className="flex items-start justify-between gap-2">
        <button onClick={onShow} className="text-left text-sm hover:underline" title="Show in PDF">
          <b>{table.label ?? "Table"}</b>{" "}
          <span className="text-zinc-600 dark:text-zinc-400">
            {table.caption.replace(/^Table \d+[:.]?\s*/, "").slice(0, 160)}
          </span>
          <span className="ml-1 text-xs text-zinc-400">p. {table.page}</span>
        </button>
        <button
          onClick={download}
          className="shrink-0 rounded border border-zinc-300 px-2 py-0.5 text-xs hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-800"
        >
          CSV{edited ? ` (${edited} edited)` : ""}
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full border-collapse text-xs">
          <thead>
            <tr className="border-b border-zinc-300 dark:border-zinc-700">
              <th className="px-1.5 py-1 text-left font-medium">Method</th>
              {numeric.map((c) => (
                <th key={c.index} className="px-1.5 py-1 text-right font-medium" title={c.group}>
                  {c.group && <div className="font-normal text-zinc-400">{c.group}</div>}
                  {c.header}
                  {c.higher_is_better !== null && (
                    <span className="ml-0.5 text-zinc-400">{c.higher_is_better ? "↑" : "↓"}</span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {table.rows.map((r, i) => {
              const byCol = new Map(r.cells.map((c) => [c.col, c]));
              const newGroup = r.group && r.group !== table.rows[i - 1]?.group;
              return [
                newGroup ? (
                  <tr key={`g${r.index}`}>
                    <td colSpan={numeric.length + 1} className="px-1.5 pt-2 italic text-zinc-500">
                      {r.group}
                    </td>
                  </tr>
                ) : null,
                <tr
                  key={r.index}
                  className={`border-b border-zinc-100 dark:border-zinc-800 ${
                    r.is_proposed ? "bg-sky-50 dark:bg-sky-950/40" : ""
                  }`}
                >
                  <Cell
                    value={text(r.index, -1, r.label)}
                    onChange={(v) => setEdits({ ...edits, [`${r.index}:-1`]: v })}
                    className="text-left"
                  />
                  {numeric.map((c) => {
                    const cell = byCol.get(c.index);
                    return (
                      <Cell
                        key={c.index}
                        value={text(r.index, c.index, cell?.text ?? "")}
                        onChange={(v) => setEdits({ ...edits, [`${r.index}:${c.index}`]: v })}
                        className={`text-right tabular-nums ${
                          cell?.is_best
                            ? "bg-emerald-100 font-semibold text-emerald-900 dark:bg-emerald-900/40 dark:text-emerald-200"
                            : ""
                        } ${cell?.is_bold ? "underline decoration-dotted" : ""}`}
                        title={cell?.is_bold ? "bold in the paper" : undefined}
                      />
                    );
                  })}
                </tr>,
              ];
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function Cell({
  value,
  onChange,
  className,
  title,
}: {
  value: string;
  onChange: (v: string) => void;
  className: string;
  title?: string;
}) {
  return (
    <td className={`px-1.5 py-0.5 ${className}`} title={title}>
      {/* Sized to its text so labels and "88.5±1.1" are never cut off. */}
      <input
        value={value}
        size={Math.max(3, value.length)}
        onChange={(e) => onChange(e.target.value)}
        className="bg-transparent text-inherit outline-none focus:ring-1 focus:ring-sky-400"
        style={{ textAlign: "inherit" }}
      />
    </td>
  );
}
