"use client";

import { useMutation } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { askPaper, type ChatAnswer, type ChatTurn, type Citation } from "@/lib/api";
import type { EvidenceTarget } from "./overview";

type Message = { role: "user"; text: string } | { role: "assistant"; reply: ChatAnswer };

const STARTERS = [
  "What problem does the paper solve?",
  "Which datasets and metrics are used?",
  "What hyperparameters are used for training?",
  "What are the limitations?",
];

/** Grounded chat (M11): answers cite passages as [P1]; each becomes a page chip that
 * highlights the passage in the PDF. The conversation is kept in this browser only. */
export function ChatView({
  paperId,
  activeKey,
  onEvidence,
}: {
  paperId: string;
  activeKey: string | null;
  onEvidence: (target: EvidenceTarget) => void;
}) {
  const storageKey = `paperlens-chat-${paperId}`;
  const [messages, setMessages] = useState<Message[]>(() => {
    try {
      const saved = sessionStorage.getItem(storageKey);
      return saved ? (JSON.parse(saved) as Message[]) : [];
    } catch {
      return [];
    }
  });
  const [question, setQuestion] = useState("");
  const bottom = useRef<HTMLDivElement>(null);

  useEffect(() => {
    try {
      sessionStorage.setItem(storageKey, JSON.stringify(messages.slice(-30)));
    } catch {
      // storage blocked (private window): the chat still works, it is just not kept
    }
    bottom.current?.scrollIntoView({ block: "end" });
  }, [messages, storageKey]);

  const ask = useMutation({
    mutationFn: (q: string) => {
      const history: ChatTurn[] = messages.map((m) =>
        m.role === "user"
          ? { role: "user", content: m.text }
          : { role: "assistant", content: m.reply.answer },
      );
      return askPaper(paperId, q, history);
    },
    onSuccess: (reply) => setMessages((m) => [...m, { role: "assistant", reply }]),
  });

  const send = (q: string) => {
    const text = q.trim();
    if (!text || ask.isPending) return;
    setMessages((m) => [...m, { role: "user", text }]);
    setQuestion("");
    ask.mutate(text);
  };

  return (
    <div className="flex h-full min-h-[60vh] flex-col gap-3">
      <div className="flex-1 space-y-3">
        {messages.length === 0 && (
          <div className="space-y-2 text-xs text-zinc-500">
            <p>
              Ask about this paper. Answers come only from the paper and cite the passages they use;
              if the paper does not say, the answer says so.
            </p>
            <div className="flex flex-wrap gap-1.5">
              {STARTERS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="rounded-full border border-zinc-300 px-2.5 py-1 hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-800"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) =>
          m.role === "user" ? (
            <p
              key={i}
              className="ml-8 rounded-lg bg-zinc-100 px-3 py-2 dark:bg-zinc-800"
              data-role="user"
            >
              {m.text}
            </p>
          ) : (
            <Reply
              key={i}
              index={i}
              reply={m.reply}
              activeKey={activeKey}
              onEvidence={onEvidence}
            />
          ),
        )}
        {ask.isPending && <p className="text-xs text-zinc-500">Searching the paper…</p>}
        {ask.isError && <p className="text-xs text-red-600">{ask.error.message}</p>}
        <div ref={bottom} />
      </div>
      <form
        className="sticky bottom-0 flex gap-2 bg-white pt-1 dark:bg-zinc-950"
        onSubmit={(e) => {
          e.preventDefault();
          send(question);
        }}
      >
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about the paper"
          maxLength={1000}
          className="min-w-0 flex-1 rounded-lg border border-zinc-300 bg-transparent px-3 py-2 text-sm outline-none focus:border-sky-500 dark:border-zinc-700"
        />
        <button
          type="submit"
          disabled={ask.isPending || !question.trim()}
          className="rounded-lg bg-zinc-900 px-3 py-2 text-sm text-white disabled:opacity-40 dark:bg-zinc-100 dark:text-zinc-900"
        >
          Ask
        </button>
        {messages.length > 0 && (
          <button
            type="button"
            onClick={() => setMessages([])}
            className="text-xs text-zinc-500 hover:underline"
          >
            Clear
          </button>
        )}
      </form>
    </div>
  );
}

function Reply({
  index,
  reply,
  activeKey,
  onEvidence,
}: {
  index: number;
  reply: ChatAnswer;
  activeKey: string | null;
  onEvidence: (target: EvidenceTarget) => void;
}) {
  const byMarker = new Map(reply.citations.map((c) => [c.marker, c]));
  const show = (c: Citation) =>
    onEvidence({
      itemId: `chat:${index}:${c.marker}`,
      index: 0,
      evidence: {
        chunk_id: c.chunk_id,
        page: c.page,
        bbox: null,
        boxes: c.boxes,
        quote: c.text,
        grounding_status: "verified",
        match_score: null,
      },
    });
  // "They train for 100 epochs [P2]." -> text with a page chip in place of [P2].
  const parts = reply.answer.split(/(\[P\d+\])/g);
  return (
    <div
      className={`mr-4 space-y-1.5 rounded-lg border px-3 py-2 ${
        reply.answered
          ? "border-zinc-200 dark:border-zinc-800"
          : "border-amber-300 bg-amber-50 text-amber-900 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-200"
      }`}
      data-role="assistant"
      data-answered={reply.answered}
    >
      <p className="leading-relaxed">
        {parts.map((part, i) => {
          const marker = part.match(/^\[(P\d+)\]$/)?.[1];
          const c = marker ? byMarker.get(marker) : undefined;
          if (!c) return <span key={i}>{part}</span>;
          const active = activeKey === `chat:${index}:${c.marker}#0`;
          return (
            <button
              key={i}
              onClick={() => show(c)}
              title={`${c.section} · page ${c.page}\n\n${c.text}`}
              className={`citation-chip mx-0.5 rounded px-1 align-baseline text-[11px] font-medium ${
                active
                  ? "bg-emerald-600 text-white"
                  : "bg-emerald-100 text-emerald-900 hover:bg-emerald-200 dark:bg-emerald-900/50 dark:text-emerald-200"
              }`}
            >
              p. {c.page}
            </button>
          );
        })}
      </p>
      <p className="text-[10px] text-zinc-400">
        {reply.answered ? `${reply.citations.length} passage(s) cited` : "not answered"} ·{" "}
        {reply.retrieval === "hybrid" ? "keyword + meaning search" : "keyword search only"}
        {reply.model && ` · ${reply.model}`}
      </p>
    </div>
  );
}
