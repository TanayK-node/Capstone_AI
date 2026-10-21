"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { listPapers } from "@/lib/api";
import { StatusBadge } from "./status-badge";

export function PaperList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["papers"],
    queryFn: listPapers,
    refetchInterval: (q) =>
      q.state.data?.some((p) => p.status === "queued" || p.status === "processing") ? 2000 : false,
  });

  if (isLoading) return <p className="text-sm text-zinc-500">Loading library…</p>;
  if (error) return <p className="text-sm text-red-600">Could not load papers: {error.message}</p>;
  if (!data?.length) return <p className="text-sm text-zinc-500">No papers yet.</p>;

  return (
    <ul className="divide-y divide-zinc-200 rounded-xl border border-zinc-200 dark:divide-zinc-800 dark:border-zinc-800">
      {data.map((p) => (
        <li key={p.id}>
          <Link
            href={`/papers/${p.id}`}
            className="flex items-center justify-between gap-4 px-4 py-3 hover:bg-zinc-50 dark:hover:bg-zinc-900"
          >
            <div className="min-w-0">
              <p className="truncate font-medium">{p.title ?? "Untitled paper"}</p>
              <p className="text-xs text-zinc-500">
                {p.source_type}
                {p.source_id ? ` · ${p.source_id}` : ""} · {p.page_count} pages
              </p>
            </div>
            <StatusBadge status={p.status} />
          </Link>
        </li>
      ))}
    </ul>
  );
}
