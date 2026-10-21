import { HealthPanel } from "@/components/health-panel";

export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-10 px-6 py-16">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold tracking-tight">PaperLens</h1>
        <p className="text-zinc-600 dark:text-zinc-400">
          Not just what the paper says, but whether you can reproduce it.
        </p>
      </header>
      <HealthPanel />
    </main>
  );
}
