import type { TableData } from "@/lib/api";

/** Renders a parsed table: header rows shaded, bold cells bold, parsed numbers in tooltips. */
export function TableView({ table }: { table: TableData }) {
  const rows: (TableData["cells"][number] | undefined)[][] = Array.from(
    { length: table.n_rows },
    () => Array(table.n_cols).fill(undefined),
  );
  for (const c of table.cells)
    if (c.row < table.n_rows && c.col < table.n_cols) rows[c.row][c.col] = c;

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-xs">
        <tbody>
          {rows.map((row, r) => (
            <tr key={r} className={r < table.header_rows ? "bg-zinc-100 dark:bg-zinc-800" : ""}>
              {row.map((cell, c) => (
                <td
                  key={c}
                  title={
                    cell?.value != null
                      ? `value=${cell.value}${cell.std != null ? ` std=${cell.std}` : ""}${cell.is_percent ? " (%)" : ""}`
                      : undefined
                  }
                  className={`border border-zinc-200 px-2 py-1 dark:border-zinc-700 ${
                    cell?.is_bold ? "font-bold" : ""
                  } ${cell?.value != null ? "text-right tabular-nums" : ""}`}
                >
                  {cell?.text}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
