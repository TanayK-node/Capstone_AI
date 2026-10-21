import { Suspense } from "react";
import { Workspace } from "@/components/workspace";

export default function PaperPage() {
  return (
    <Suspense fallback={<p className="p-6 text-sm text-zinc-500">Loading…</p>}>
      <Workspace />
    </Suspense>
  );
}
