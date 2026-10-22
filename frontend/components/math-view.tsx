"use client";

import katex from "katex";
import "katex/dist/katex.min.css";
import { useMemo, useState } from "react";
import type { Equation, MathReport } from "@/lib/api";
import { EvidenceChip, type EvidenceTarget } from "./overview";

/** LaTeX -> HTML. KaTeX never runs code; on a parse error we fall back to the plain source,
 * so a macro the paper defines in a way KaTeX cannot read shows as text, not as an error. */
function render(latex: string, macros: Record<string, string>, display: boolean): string | null {
  try {
    // KaTeX writes \gdef definitions into the macros object: give it a copy.
    return katex.renderToString(latex, {
      displayMode: display,
      macros: { ...macros },
      throwOnError: true,
      strict: "ignore",
      trust: false,
    });
  } catch {
    return null;
  }
}

function Tex({
  latex,
  macros,
  display = false,
}: {
  latex: string;
  macros: Record<string, string>;
  display?: boolean;
}) {
  const html = useMemo(() => render(latex, macros, display), [latex, macros, display]);
  if (html === null)
    return <code className="whitespace-pre-wrap break-all text-[11px] text-zinc-600">{latex}</code>;
  return <span dangerouslySetInnerHTML={{ __html: html }} />;
}

/** Equations and notation (M10): equations from the arXiv LaTeX when available (else the
 * PDF text), the glossary with each symbol's defining sentence as evidence. */
export function MathView({
  report,
  activeKey,
  onEvidence,
}: {
  report: MathReport;
  activeKey: string | null;
  onEvidence: (target: EvidenceTarget) => void;
}) {
  const [focus, setFocus] = useState<string | null>(null); // symbol whose equations are marked
  const [query, setQuery] = useState("");
  const macros = report.macros;
  const marked = new Set(report.symbols.find((s) => s.symbol === focus)?.equations ?? []);

  const showEquation = (eq: Equation) => {
    if (!eq.block_id || !eq.boxes.length) return;
    onEvidence({
      itemId: `eq:${eq.id}`,
      index: 0,
      evidence: {
        chunk_id: eq.block_id,
        page: eq.page ?? eq.boxes[0].page,
        bbox: null,
        boxes: eq.boxes,
        quote: eq.text,
        grounding_status: "verified",
        match_score: null,
      },
    });
  };

  const q = query.trim().toLowerCase();
  const symbols = report.symbols.filter(
    (s) => !q || s.symbol.toLowerCase().includes(q) || s.meaning.toLowerCase().includes(q),
  );

  return (
    <div className="space-y-5">
      <p className="text-xs text-zinc-500">
        {report.latex_available
          ? "Equations rendered from the paper's LaTeX source (arXiv), with its own macros."
          : "No LaTeX source: equations are shown as the PDF text."}{" "}
        Click a numbered equation to find it in the PDF.
      </p>
      {report.warnings.map((w) => (
        <p key={w} className="text-xs text-amber-700 dark:text-amber-400">
          ⚠ {w}
        </p>
      ))}

      <section className="space-y-2">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h3 className="font-medium">Notation ({report.symbols.length})</h3>
          {report.symbols.length > 8 && (
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Filter symbols…"
              className="rounded border border-zinc-300 bg-transparent px-2 py-1 text-xs dark:border-zinc-700"
            />
          )}
        </div>
        {report.symbols.length === 0 ? (
          <p className="text-xs text-zinc-500">No glossary (see the warnings above).</p>
        ) : (
          <ul className="divide-y divide-zinc-100 dark:divide-zinc-800">
            {symbols.map((s) => (
              <li
                key={s.symbol}
                className={`space-y-1 py-2 ${focus === s.symbol ? "bg-amber-50 dark:bg-amber-950/30" : ""}`}
              >
                <div className="flex items-baseline gap-3">
                  <button
                    type="button"
                    onClick={() => setFocus(focus === s.symbol ? null : s.symbol)}
                    title={
                      s.equations.length
                        ? `Mark the ${s.equations.length} equation(s) that use it`
                        : "Not found in the equations"
                    }
                    className="min-w-12 shrink-0 text-left text-base"
                  >
                    <Tex latex={s.symbol} macros={macros} />
                  </button>
                  <span className="flex-1">{s.meaning}</span>
                  {s.equations.length > 0 && (
                    <span className="shrink-0 text-[11px] text-zinc-500">
                      in {s.equations.length} eq.
                    </span>
                  )}
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {s.evidence.map((ev, i) => (
                    <EvidenceChip
                      key={i}
                      evidence={ev}
                      active={activeKey === `sym:${s.symbol}#${i}`}
                      onClick={() =>
                        onEvidence({ itemId: `sym:${s.symbol}`, index: i, evidence: ev })
                      }
                    />
                  ))}
                  {s.evidence.length === 0 && (
                    <span className="text-[11px] text-zinc-500">
                      no defining sentence: unverified
                    </span>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="space-y-2">
        <h3 className="font-medium">Equations ({report.equations.length})</h3>
        {report.equations.length === 0 && (
          <p className="text-xs text-zinc-500">No display equations found.</p>
        )}
        <ul className="space-y-1">
          {report.equations.map((eq) => {
            const located = Boolean(eq.block_id && eq.boxes.length);
            const active = activeKey === `eq:${eq.id}#0`;
            return (
              <li key={eq.id}>
                <button
                  type="button"
                  onClick={() => showEquation(eq)}
                  disabled={!located}
                  title={located ? `Show on page ${eq.page}` : "Not matched to the PDF"}
                  className={`flex w-full items-center gap-2 rounded border px-2 py-1 text-left disabled:cursor-default ${
                    active
                      ? "border-emerald-500 bg-emerald-50 dark:bg-emerald-950/30"
                      : marked.has(eq.id)
                        ? "border-amber-400 bg-amber-50 dark:bg-amber-950/30"
                        : "border-transparent hover:border-zinc-200 dark:hover:border-zinc-700"
                  }`}
                >
                  <div className="min-w-0 flex-1 overflow-x-auto">
                    {eq.latex ? (
                      <Tex latex={eq.latex} macros={macros} display />
                    ) : (
                      <code className="whitespace-pre-wrap text-xs">{eq.text}</code>
                    )}
                  </div>
                  <span className="shrink-0 text-xs text-zinc-500">
                    {eq.number}
                    {located ? ` · p. ${eq.page}` : ""}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      </section>
    </div>
  );
}
