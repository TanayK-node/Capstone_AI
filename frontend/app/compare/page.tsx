import { Suspense } from "react";
import { CompareView } from "@/components/compare-view";

export default function ComparePage() {
  return (
    <Suspense fallback={<p className="p-6 text-sm text-zinc-500">Loading…</p>}>
      <CompareView />
    </Suspense>
  );
}
