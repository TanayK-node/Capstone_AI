"use client";

// Must be loaded with next/dynamic { ssr: false }: PDF.js needs browser APIs.
import { useEffect, useRef, useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import type { Block, Box, PageInfo } from "@/lib/api";
import { BLOCK_COLORS, mergeBoxes } from "@/lib/blocks";

// react-pdf: the worker must be configured in the same module that renders <Document>.
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url,
).toString();

/** Evidence to highlight, drawn on its own layer above the (optional) block overlay. */
export type Highlight = { key: string; boxes: Box[]; color: string };

type Props = {
  url: string;
  pages: PageInfo[];
  blocks: Block[];
  visibleTypes: Set<string>;
  selectedId: string | null;
  onSelect: (id: string) => void;
  highlight?: Highlight | null;
};

export default function PdfViewer({
  url,
  pages,
  blocks,
  visibleTypes,
  selectedId,
  onSelect,
  highlight = null,
}: Props) {
  const container = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(600);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const el = container.current;
    if (!el) return;
    const observer = new ResizeObserver(([entry]) =>
      setWidth(Math.max(300, Math.floor(entry.contentRect.width) - 16)),
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    document
      .getElementById(`box-${selectedId}`)
      ?.scrollIntoView({ block: "center", behavior: "smooth" });
  }, [selectedId]);

  useEffect(() => {
    if (!highlight) return;
    document
      .getElementById("evidence-highlight-0")
      ?.scrollIntoView({ block: "center", behavior: "smooth" });
  }, [highlight]);

  const highlightBoxes = highlight ? mergeBoxes(highlight.boxes) : [];

  const byPage = new Map<number, Block[]>();
  for (const b of blocks) {
    if (!visibleTypes.has(b.type) && b.id !== selectedId) continue;
    for (const box of b.boxes.length ? b.boxes : b.bbox ? [b.bbox] : []) {
      const list = byPage.get(box.page) ?? [];
      if (!list.includes(b)) list.push(b);
      byPage.set(box.page, list);
    }
  }

  return (
    <div ref={container} className="h-full overflow-y-auto bg-zinc-100 p-2 dark:bg-zinc-900">
      {error && <p className="p-4 text-sm text-red-600">Could not load the PDF: {error}</p>}
      <Document file={url} onLoadError={(e) => setError(e.message)} loading={null}>
        {pages.map((info) => (
          <LazyPage
            key={info.number}
            info={info}
            width={width}
            blocks={byPage.get(info.number) ?? []}
            selectedId={selectedId}
            onSelect={onSelect}
            highlight={highlight}
            highlightBoxes={highlightBoxes}
          />
        ))}
      </Document>
    </div>
  );
}

function LazyPage({
  info,
  width,
  blocks,
  selectedId,
  onSelect,
  highlight,
  highlightBoxes,
}: {
  info: PageInfo;
  width: number;
  blocks: Block[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  highlight: Highlight | null;
  highlightBoxes: Box[];
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [seen, setSeen] = useState(info.number <= 2);
  const scale = width / info.width;
  const height = info.height * scale;

  useEffect(() => {
    if (seen || !ref.current) return;
    const observer = new IntersectionObserver(([entry]) => entry.isIntersecting && setSeen(true), {
      rootMargin: "1200px 0px",
    });
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [seen]);

  return (
    <div
      ref={ref}
      className="relative mx-auto mb-2 bg-white shadow-sm"
      style={{ width, height }}
      data-page={info.number}
    >
      {seen && (
        <Page
          pageNumber={info.number}
          width={width}
          renderTextLayer={false}
          renderAnnotationLayer={false}
          loading={null}
        />
      )}
      <div className="pointer-events-none absolute inset-0">
        {blocks.flatMap((b) =>
          mergeBoxes(b.boxes.length ? b.boxes : b.bbox ? [b.bbox] : [])
            .filter((box) => box.page === info.number)
            .map((box, i) => {
              const color = BLOCK_COLORS[b.type] ?? "#6b7280";
              const selected = b.id === selectedId;
              return (
                <button
                  key={`${b.id}-${i}`}
                  id={i === 0 ? `box-${b.id}` : undefined}
                  type="button"
                  title={`${b.id} · ${b.type}${b.role ? ` · ${b.role}` : ""}`}
                  onClick={() => onSelect(b.id)}
                  className="pointer-events-auto absolute rounded-[2px] transition-colors"
                  style={{
                    left: box.x0 * scale,
                    top: box.y0 * scale,
                    width: (box.x1 - box.x0) * scale,
                    height: (box.y1 - box.y0) * scale,
                    border: `${selected ? 2 : 1}px solid ${color}`,
                    background: selected ? `${color}40` : `${color}14`,
                  }}
                />
              );
            }),
        )}
      </div>
      {highlight && (
        <div className="pointer-events-none absolute inset-0">
          {highlightBoxes.map((box, i) =>
            box.page === info.number ? (
              <div
                key={`${highlight.key}-${i}`}
                id={`evidence-highlight-${i}`}
                className="evidence-highlight absolute rounded-[2px]"
                style={{
                  left: box.x0 * scale - 2,
                  top: box.y0 * scale - 2,
                  width: (box.x1 - box.x0) * scale + 4,
                  height: (box.y1 - box.y0) * scale + 4,
                  background: `${highlight.color}33`,
                  outline: `2px solid ${highlight.color}`,
                  mixBlendMode: "multiply",
                }}
              />
            ) : null,
          )}
        </div>
      )}
    </div>
  );
}
