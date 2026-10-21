"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { createPaper } from "@/lib/api";

export function UploadCard() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const fileInput = useRef<HTMLInputElement>(null);
  const [url, setUrl] = useState("");
  const [dragging, setDragging] = useState(false);

  const mutation = useMutation({
    mutationFn: createPaper,
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["papers"] });
      router.push(`/papers/${res.paper_id}`);
    },
  });

  const submitFile = (file: File | undefined) => {
    if (file) mutation.mutate({ file });
  };

  return (
    <section className="space-y-4 rounded-xl border border-zinc-200 p-6 dark:border-zinc-800">
      <div
        role="button"
        tabIndex={0}
        onClick={() => fileInput.current?.click()}
        onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && fileInput.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          submitFile(e.dataTransfer.files[0]);
        }}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-10 text-center transition ${
          dragging
            ? "border-sky-500 bg-sky-50 dark:bg-sky-950/30"
            : "border-zinc-300 hover:border-zinc-400 dark:border-zinc-700"
        }`}
      >
        <p className="font-medium">Drop a PDF here, or click to choose one</p>
        <p className="mt-1 text-sm text-zinc-500">Up to 50 MB and 100 pages</p>
        <input
          ref={fileInput}
          type="file"
          accept="application/pdf,.pdf"
          className="hidden"
          onChange={(e) => submitFile(e.target.files?.[0])}
        />
      </div>

      <form
        className="flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          if (url.trim()) mutation.mutate({ url: url.trim() });
        }}
      >
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="arXiv id or link, DOI, OpenReview, ACL Anthology, or PDF URL"
          className="min-w-0 flex-1 rounded-lg border border-zinc-300 bg-transparent px-3 py-2 text-sm outline-none focus:border-sky-500 dark:border-zinc-700"
        />
        <button
          type="submit"
          disabled={mutation.isPending || !url.trim()}
          className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-40 dark:bg-zinc-100 dark:text-zinc-900"
        >
          Analyze
        </button>
      </form>

      <p className="text-xs text-zinc-500">
        Privacy: the paper&apos;s text is sent to the Google Gemini API (free tier) for extraction.
        Google may use free-tier inputs to improve its models, so do not upload unpublished or
        confidential papers.
      </p>

      {mutation.isPending && (
        <p className="text-sm text-zinc-500">Fetching and checking the PDF…</p>
      )}
      {mutation.isError && <p className="text-sm text-red-600">{mutation.error.message}</p>}
    </section>
  );
}
