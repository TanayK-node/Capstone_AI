"use client";

import type { ChecklistResult, ItemStatus, ReproResponse, Scorecard } from "@/lib/api";
import { EvidenceChip, type EvidenceTarget } from "./overview";

const STATUS: Record<ItemStatus, { label: string; color: string }> = {
  present: { label: "Present", color: "#059669" },
  partial: { label: "Partial", color: "#d97706" },
  missing: { label: "Missing", color: "#dc2626" },
  not_applicable: { label: "N/A", color: "#6b7280" },
  unknown: { label: "Unknown", color: "#6b7280" },
};

const SOURCE: Record<ChecklistResult["source"], string> = {
  rule: "rule",
  extraction: "from Overview",
  repo: "GitHub",
  llm: "Gemini",
  none: "",
};

function scoreColor(score: number) {
  return score >= 70 ? "#059669" : score >= 40 ? "#d97706" : "#dc2626";
}

export function ReproView({
  repro,
  activeKey,
  onEvidence,
}: {
  repro: ReproResponse;
  activeKey: string | null;
  onEvidence: (target: EvidenceTarget) => void;
}) {
  const card = repro.scorecard;
  return (
    <div className="space-y-5">
      <ScoreHeader card={card} />
      {card.repo && <RepoCard card={card} />}

      {card.groups.map((g) => (
        <section key={g.id} className="space-y-2">
          <h3 className="flex items-baseline justify-between text-xs font-semibold uppercase tracking-wide text-zinc-500">
            <span>{g.label}</span>
            <span className="font-normal normal-case">
              {g.score === null ? "not scored" : `${Math.round(g.score * 100)}%`}
            </span>
          </h3>
          <ul className="space-y-2">
            {card.items
              .filter((i) => i.group === g.id)
              .map((item) => (
                <ChecklistRow
                  key={item.id}
                  item={item}
                  activeKey={activeKey}
                  onEvidence={onEvidence}
                />
              ))}
          </ul>
        </section>
      ))}

      {card.questions.length > 0 && (
        <section className="space-y-2 rounded-lg border border-zinc-200 p-3 dark:border-zinc-800">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
            Missing for reproduction: questions for the authors
          </h3>
          <ol className="ml-4 list-decimal space-y-1">
            {card.questions.map((q) => (
              <li key={q}>{q}</li>
            ))}
          </ol>
        </section>
      )}

      {card.warnings.length > 0 && (
        <div className="text-[11px] text-amber-700 dark:text-amber-400">
          {card.warnings.map((w) => (
            <p key={w}>⚠ {w}</p>
          ))}
        </div>
      )}
      <p className="text-[11px] text-zinc-400">
        Checklist v{card.checklist_version}
        {repro.model && ` · ${repro.model}`}
        {repro.prompt_version && ` · ${repro.prompt_version}`}
      </p>
    </div>
  );
}

function ScoreHeader({ card }: { card: Scorecard }) {
  const score = card.score;
  const counts: Partial<Record<ItemStatus, number>> = {};
  for (const i of card.items) counts[i.status] = (counts[i.status] ?? 0) + 1;
  return (
    <section className="flex flex-wrap items-center gap-5 rounded-lg border border-zinc-200 p-3 dark:border-zinc-800">
      <div className="text-center">
        <div
          className="text-4xl font-semibold tabular-nums"
          style={{ color: score === null ? undefined : scoreColor(score) }}
        >
          {score === null ? "–" : Math.round(score)}
        </div>
        <div className="text-[11px] text-zinc-500">reproducibility / 100</div>
      </div>
      <div className="min-w-48 flex-1 space-y-1.5">
        {card.groups.map((g) => (
          <div key={g.id} className="flex items-center gap-2 text-[11px]">
            <span className="w-28 shrink-0 truncate text-zinc-600 dark:text-zinc-400">
              {g.label}
            </span>
            <div className="h-2 flex-1 overflow-hidden rounded bg-zinc-100 dark:bg-zinc-800">
              {g.score !== null && (
                <div
                  className="h-full rounded"
                  style={{
                    width: `${Math.round(g.score * 100)}%`,
                    background: scoreColor(g.score * 100),
                  }}
                />
              )}
            </div>
            <span className="w-8 text-right tabular-nums">
              {g.score === null ? "–" : Math.round(g.score * 100)}
            </span>
          </div>
        ))}
        <div className="flex flex-wrap gap-x-3 pt-1 text-[11px] text-zinc-500">
          {(Object.keys(STATUS) as ItemStatus[])
            .filter((s) => counts[s])
            .map((s) => (
              <span key={s} className="flex items-center gap-1">
                <span
                  className="inline-block h-2 w-2 rounded-full"
                  style={{ background: STATUS[s].color }}
                />
                {STATUS[s].label} {counts[s]}
              </span>
            ))}
        </div>
      </div>
    </section>
  );
}

function RepoCard({ card }: { card: Scorecard }) {
  const repo = card.repo!;
  return (
    <p className="text-xs text-zinc-600 dark:text-zinc-400">
      Code:{" "}
      <a
        href={repo.url}
        target="_blank"
        rel="noreferrer"
        className="text-sky-700 underline dark:text-sky-400"
      >
        {repo.url.replace(/^https?:\/\//, "")}
      </a>
      {repo.reachable && (
        <>
          {repo.license && ` · ${repo.license}`}
          {repo.stars !== null && ` · ★ ${repo.stars}`}
          {repo.pushed_at && ` · last push ${repo.pushed_at.slice(0, 10)}`}
          {repo.archived && " · archived"}
        </>
      )}
      {repo.error && <span className="text-amber-700 dark:text-amber-400"> · {repo.error}</span>}
    </p>
  );
}

function ChecklistRow({
  item,
  activeKey,
  onEvidence,
}: {
  item: ChecklistResult;
  activeKey: string | null;
  onEvidence: (target: EvidenceTarget) => void;
}) {
  const st = STATUS[item.status];
  const key = `repro:${item.id}`;
  return (
    <li className="space-y-1" data-item={item.id}>
      <div className="flex items-start gap-2">
        <span
          className="mt-0.5 w-16 shrink-0 rounded px-1.5 py-0.5 text-center text-[10px] font-medium text-white"
          style={{ background: st.color }}
        >
          {st.label}
        </span>
        <div className="min-w-0 flex-1">
          <p className="leading-snug">{item.description}</p>
          {(item.note || SOURCE[item.source]) && (
            <p className="text-[11px] text-zinc-500">
              {SOURCE[item.source] && (
                <span className="mr-1 rounded bg-zinc-100 px-1 dark:bg-zinc-800">
                  {SOURCE[item.source]}
                </span>
              )}
              {item.note}
            </p>
          )}
        </div>
      </div>
      {item.evidence.length > 0 && (
        <div className="ml-[4.5rem] flex flex-wrap gap-1">
          {item.evidence.map((ev, i) => (
            <EvidenceChip
              key={i}
              evidence={ev}
              active={activeKey === `${key}#${i}`}
              onClick={() => onEvidence({ itemId: key, index: i, evidence: ev })}
            />
          ))}
        </div>
      )}
    </li>
  );
}
