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
      </header>
      <UploadCard />
      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Library</h2>
        <PaperList />
      </section>
      <HealthPanel />
    </main>
  );
}
