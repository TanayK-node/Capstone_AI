import Link from "next/link";
import { HealthPanel } from "@/components/health-panel";
import { PaperList } from "@/components/paper-list";
import { UploadCard } from "@/components/upload-card";

export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-10 px-6 py-12">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold tracking-tight">PaperLens</h1>
        <p className="text-zinc-600 dark:text-zinc-400">
          Not just what the paper says, but whether you can reproduce it.
        </p>
        <p className="text-sm text-zinc-500">
          Upload a paper to get its datasets, metrics and hyperparameters with the sentence each
          comes from, a reproducibility scorecard, claims checked against its own tables, the code
          repository compared with the paper, a glossary of its notation, its key references, and a
          chat that cites pages.
        </p>
      </header>
      <UploadCard />
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Library</h2>
          <Link
            href="/compare"
            className="rounded border border-zinc-300 px-2 py-1 text-sm hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-800"
          >
            Compare papers
          </Link>
        </div>
        <PaperList />
      </section>
      <HealthPanel />
    </main>
  );
}
