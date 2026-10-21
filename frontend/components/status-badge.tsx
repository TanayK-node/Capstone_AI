const STYLES: Record<string, string> = {
  ready: "bg-emerald-100 text-emerald-900 dark:bg-emerald-900/40 dark:text-emerald-200",
  done: "bg-emerald-100 text-emerald-900 dark:bg-emerald-900/40 dark:text-emerald-200",
  processing: "bg-sky-100 text-sky-900 dark:bg-sky-900/40 dark:text-sky-200",
  running: "bg-sky-100 text-sky-900 dark:bg-sky-900/40 dark:text-sky-200",
  queued: "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300",
  partial: "bg-amber-100 text-amber-900 dark:bg-amber-900/40 dark:text-amber-200",
  failed: "bg-red-100 text-red-900 dark:bg-red-900/40 dark:text-red-200",
};

export function StatusBadge({ status, label }: { status: string; label?: string }) {
  return (
    <span
      className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${STYLES[status] ?? STYLES.queued}`}
    >
      {label ? `${label}: ${status}` : status}
    </span>
  );
}
