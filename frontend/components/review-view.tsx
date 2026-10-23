"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getReview, writeReview, type ReviewPoint } from "@/lib/api";
import { EvidenceChip, type EvidenceTarget } from "./overview";

const SOURCE_LABELS = {
  reproducibility: "Reproducibility",
  claims: "Claims",
  code: "Code",
} as const;

/** Reviewer mode (F15): written on request (one Gemini call). Points quote the paper; the
 * "facts" come from the analyses (Python), shown apart from the model's text. */
export function ReviewView({
  paperId,
  ready,
  activeKey,
  onEvidence,
}: {
  paperId: string;
  ready: boolean;
  activeKey: string | null;
  onEvidence: (target: EvidenceTarget) => void;
}) {
  const queryClient = useQueryClient();
  const review = useQuery({ queryKey: ["review", paperId], queryFn: () => getReview(paperId) });
  const write = useMutation({
    mutationFn: () => writeReview(paperId),
    onSuccess: (data) => queryClient.setQueryData(["review", paperId], data),
  });

  const button = (label: string) => (
    <button
      type="button"
      onClick={() => write.mutate()}
      disabled={!ready || write.isPending}
      className="rounded-lg border border-zinc-300 px-3 py-1.5 text-xs disabled:opacity-40 dark:border-zinc-700"
    >
      {write.isPending ? "Writing the review…" : label}
    </button>
  );

  if (review.isLoading) return <p className="text-zinc-500">Loading…</p>;
  const data = review.data;
  if (!data)
    return (
      <div className="space-y-3">
        <p className="text-zinc-500">
          An OpenReview-style review: summary, strengths, weaknesses, missing ablations and
          questions, built from the paper and from the reproducibility, claim and code checks. It
          uses one Gemini call, so it is written only when you ask.
        </p>
        {!ready && (
          <p className="text-xs text-zinc-500">Available once the analysis has finished.</p>
        )}
        {button("Write review")}
        {write.isError && <p className="text-xs text-red-600">{write.error.message}</p>}
      </div>
    );
  const rv = data.review;

  const points = (title: string, key: string, items: ReviewPoint[]) =>
    items.length > 0 && (
      <section className="space-y-2">
        <h3 className="font-medium">{title}</h3>
        <ul className="space-y-2">
          {items.map((p, i) => (
            <li key={i} className="space-y-1">
              <p>{p.point}</p>
              <div className="flex flex-wrap gap-1.5">
                {p.evidence.map((ev, j) => (
                  <EvidenceChip
                    key={j}
                    evidence={ev}
                    active={activeKey === `rev:${key}.${i}#${j}`}
                    onClick={() =>
                      onEvidence({ itemId: `rev:${key}.${i}`, index: j, evidence: ev })
                    }
                  />
                ))}
              </div>
            </li>
          ))}
        </ul>
      </section>
    );

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-zinc-500">
        <span>
          Written by {data.model ?? "the model"} · {new Date(data.created_at).toLocaleString()} · no
          score is given
        </span>
        {button("Rewrite")}
      </div>
      {write.isError && <p className="text-xs text-red-600">{write.error.message}</p>}
      <p className="leading-relaxed">{rv.summary}</p>
      {points("Strengths", "s", rv.strengths)}
      {points("Weaknesses", "w", rv.weaknesses)}
      {points("Missing ablations", "a", rv.missing_ablations)}
      {rv.findings.length > 0 && (
        <section className="space-y-2">
          <h3 className="font-medium">Facts from the analyses</h3>
          <p className="text-[11px] text-zinc-500">
            Established in Python by the reproducibility, claim and code checks, not by the model.
          </p>
          <ul className="space-y-1">
            {rv.findings.map((f, i) => (
              <li key={i} className="flex gap-2">
                <span className="shrink-0 rounded bg-zinc-100 px-1.5 py-0.5 text-[11px] dark:bg-zinc-800">
                  {SOURCE_LABELS[f.source]}
                </span>
                <span>{f.text}</span>
              </li>
            ))}
          </ul>
        </section>
      )}
      {rv.questions.length > 0 && (
        <section className="space-y-2">
          <h3 className="font-medium">Questions for the authors</h3>
          <ol className="list-decimal space-y-1 pl-5">
            {rv.questions.map((q, i) => (
              <li key={i}>{q}</li>
            ))}
          </ol>
        </section>
      )}
    </div>
  );
}
