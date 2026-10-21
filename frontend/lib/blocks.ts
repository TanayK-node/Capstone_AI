// Overlay colours per block type (debug overlay on the PDF viewer).
export const BLOCK_COLORS: Record<string, string> = {
  title: "#7c3aed",
  heading: "#db2777",
  paragraph: "#2563eb",
  table: "#059669",
  figure: "#d97706",
  caption: "#ca8a04",
  equation: "#0891b2",
  footnote: "#64748b",
  reference: "#9ca3af",
};

export const BLOCK_TYPES = Object.keys(BLOCK_COLORS);

export const ROLE_LABELS: Record<string, string> = {
  abstract: "Abstract",
  introduction: "Introduction",
  related_work: "Related work",
  background: "Background",
  method: "Method",
  experiments: "Experiments",
  results: "Results",
  ablation: "Ablation",
  discussion: "Discussion",
  limitations: "Limitations",
  conclusion: "Conclusion",
  acknowledgements: "Acknowledgements",
  references: "References",
  appendix: "Appendix",
  other: "Other",
};

import type { Box } from "./api";

/**
 * Merge line-level boxes into one rectangle per column run, for a readable overlay.
 * Boxes join when they are on the same page, overlap horizontally by at least half the
 * narrower box, and are vertically adjacent (gap under 6pt).
 */
export function mergeBoxes(boxes: Box[]): Box[] {
  const out: Box[] = [];
  for (const b of boxes) {
    const last = out[out.length - 1];
    if (last && last.page === b.page) {
      const overlap = Math.min(last.x1, b.x1) - Math.max(last.x0, b.x0);
      const narrower = Math.min(last.x1 - last.x0, b.x1 - b.x0);
      const gap = b.y0 - last.y1;
      if (overlap >= 0.5 * narrower && gap < 6 && b.y1 > last.y0) {
        out[out.length - 1] = {
          page: b.page,
          x0: Math.min(last.x0, b.x0),
          y0: Math.min(last.y0, b.y0),
          x1: Math.max(last.x1, b.x1),
          y1: Math.max(last.y1, b.y1),
        };
        continue;
      }
    }
    out.push({ ...b });
  }
  return out;
}
