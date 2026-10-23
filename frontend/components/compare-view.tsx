"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { Fragment } from "react";
import {
  comparisonCsvUrl,
  getComparison,
  listPapers,
  type MatrixRow,
  type PaperComparison,
} from "@/lib/api";

const MAX = 10;

/**
 * Multi-paper matrix (F14): pick 2-10 analysed papers; rows are datasets, metrics, training
 * settings and baselines, with the page each paper states them on. The selection lives in
 * the URL (?ids=a,b) so a comparison can be shared or reloaded.
 */
export function CompareView() {
  const params = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const ids = (params.get("ids") ?? "").split(",").filter(Boolean);
  const papers = useQuery({ queryKey: ["papers"], queryFn: listPapers });
  const comparison = useQuery({
    queryKey: ["compare", ids],
    queryFn: () => getComparison(ids),
    enabled: ids.length >= 2,
  });

  const toggle = (id: string) => {
    const next = ids.includes(id) ? ids.filter((x) => x !== id) : [...ids, id].slice(0, MAX);
    router.replace(next.length ? `${pathname}?ids=${next.join(",")}` : pathname);
  };
  const analysed = (papers.data ?? []).filter(
    (p) => p.status === "ready" || p.status === "partial",
  );

  return (
    <main className="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-6 px-6 py-8">
      <header className="space-y-1">
        <Link href="/" className="text-sm text-zinc-500 hover:underline">
          ← Library
        </Link>
        <h1 className="text-2xl font-semibold tracking-tight">Compare papers</h1>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Built from each paper&apos;s stored extraction and results tables (no LLM). Pick 2 to{" "}
          {MAX} analysed papers.
        </p>
      </header>

      <section className="rounded-xl border border-zinc-200 p-3 dark:border-zinc-800">
        {papers.isLoading && <p className="text-sm text-zinc-500">Loading library…</p>}
        {!papers.isLoading && !analysed.length && (
          <p className="text-sm text-zinc-500">No analysed papers yet.</p>
        )}
        <ul className="grid gap-1 sm:grid-cols-2">
          {analysed.map((p) => (
            <li key={p.id}>
              <label className="flex min-w-0 cursor-pointer items-center gap-2 rounded px-2 py-1 text-sm hover:bg-zinc-50 dark:hover:bg-zinc-900">
                <input
                  type="checkbox"
                  checked={ids.includes(p.id)}
                  onChange={() => toggle(p.id)}
                  disabled={!ids.includes(p.id) && ids.length >= MAX}
                />
                <span className="truncate">{p.title ?? "Untitled paper"}</span>
              </label>
            </li>
          ))}
        </ul>
      </section>

      {ids.length < 2 && <p className="text-sm text-zinc-500">Select at least two papers.</p>}
      {comparison.isLoading && <p className="text-sm text-zinc-500">Comparing…</p>}
      {comparison.error && (
        <p className="text-sm text-red-600">Could not compare: {comparison.error.message}</p>
      )}
      {comparison.data && ids.length >= 2 && <Matrix comp={comparison.data} ids={ids} />}
    </main>
  );
}

function Matrix({ comp, ids }: { comp: PaperComparison; ids: string[] }) {
  const groups: [string, MatrixRow[]][] = [];
  for (const r of comp.rows) {
    const last = groups[groups.length - 1];
    if (last && last[0] === r.group) last[1].push(r);
    else groups.push([r.group, [r]]);
  }
  const head = (
    <tr>
      <th className="sticky left-0 z-10 bg-zinc-100 px-2 py-1 text-left dark:bg-zinc-900" />
      {comp.papers.map((p) => (
        <th key={p.id} className="min-w-44 px-2 py-1 text-left align-bottom font-medium">
          <Link href={`/papers/${p.id}`} className="hover:underline">
            {p.title}
          </Link>
          {p.year && <span className="font-normal text-zinc-500"> ({p.year})</span>}
        </th>
      ))}
    </tr>
  );
  return (
    <div className="space-y-6">
      <p className="flex flex-wrap items-center gap-2 text-xs text-zinc-500">
        <span>Rows reported by two or more papers are tinted and listed first. p. = page.</span>
        <a
          href={comparisonCsvUrl(ids)}
          className="rounded border border-zinc-300 px-2 py-0.5 hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-800"
        >
          Download CSV
        </a>
      </p>
      <div className="overflow-x-auto rounded-xl border border-zinc-200 dark:border-zinc-800">
        <table className="w-full text-sm">
          <thead className="bg-zinc-100 dark:bg-zinc-900">{head}</thead>
          <tbody>
            {groups.map(([group, rows]) => (
              <Fragment key={group}>
                <tr>
                  <td
                    colSpan={comp.papers.length + 1}
                    className="bg-zinc-50 px-2 py-1 text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:bg-zinc-950"
                  >
                    {group}
                  </td>
                </tr>
                {rows.map((r, i) => (
                  <tr
                    key={`${group}-${i}`}
                    className={`border-t border-zinc-100 dark:border-zinc-800 ${r.shared ? "bg-sky-50 dark:bg-sky-950/40" : ""}`}
                  >
                    <th className="sticky left-0 bg-inherit px-2 py-1 text-left font-normal">
                      {r.label}
                    </th>
                    {r.cells.map((c, k) => (
                      <td key={k} className="px-2 py-1 align-top">
                        {c.values.length ? (
                          <>
                            {c.values.join("; ")}
                            {c.pages.length > 0 && (
                              <span className="ml-1 text-xs text-zinc-500">
                                p. {c.pages.join(", ")}
                              </span>
                            )}
                          </>
                        ) : (
                          <span className="text-zinc-300 dark:text-zinc-700">–</span>
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>

      <section className="space-y-2">
        <h2 className="text-lg font-semibold">Shared results</h2>
        <p className="text-xs text-zinc-500">
          Table columns whose header reads the same in several papers, with each paper&apos;s own
          best value there. Matched by header text only: the setups may still differ, so check the
          tables before drawing conclusions.
        </p>
        {comp.warnings.map((w) => (
          <p key={w} className="text-sm text-zinc-500">
            {w[0].toUpperCase() + w.slice(1)}.
          </p>
        ))}
        {comp.results.length > 0 && (
          <div className="overflow-x-auto rounded-xl border border-zinc-200 dark:border-zinc-800">
            <table className="w-full text-sm">
              <thead className="bg-zinc-100 dark:bg-zinc-900">{head}</thead>
              <tbody>
                {comp.results.map((s) => (
                  <tr key={s.label} className="border-t border-zinc-100 dark:border-zinc-800">
                    <th className="sticky left-0 bg-white px-2 py-1 text-left font-normal dark:bg-zinc-950">
                      {s.label}
                      {s.higher_is_better !== null && (
                        <span className="ml-1 text-xs text-zinc-500">
                          {s.higher_is_better ? "↑" : "↓"}
                        </span>
                      )}
                    </th>
                    {s.cells.map((c, k) => (
                      <td key={k} className="px-2 py-1 align-top">
                        {c.text ? (
                          <>
                            <span className="font-medium tabular-nums">{c.text}</span>{" "}
                            <span className="text-xs text-zinc-500">
                              {c.method}
                              {c.table ? ` · ${c.table}` : ""}
                              {c.page ? `, p. ${c.page}` : ""}
                            </span>
                          </>
                        ) : (
                          <span className="text-zinc-300 dark:text-zinc-700">–</span>
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
