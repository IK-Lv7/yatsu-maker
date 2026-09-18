"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import type { Submission } from "@/app/lib/submissions";

const MEDALS = ["🥇", "🥈", "🥉"];

export default function SubmissionList({ submissions }: { submissions: Submission[] }) {
  const router = useRouter();
  const [votedIds, setVotedIds] = useState<Set<number>>(new Set());

  async function handleVote(id: number) {
    if (votedIds.has(id)) return;
    setVotedIds((prev) => new Set(prev).add(id));

    const res = await fetch(`/api/submissions/${id}/vote`, { method: "POST" });
    if (res.ok) {
      router.refresh();
    }
  }

  if (submissions.length === 0) {
    return (
      <p className="text-sm text-stone-500 rounded-xl border border-dashed border-orange-200 dark:border-stone-800 px-4 py-6 text-center">
        まだ投稿がありません。最初の投稿者になりましょう。
      </p>
    );
  }

  return (
    <ul className="flex flex-col gap-2">
      {submissions.map((s, i) => (
        <li
          key={s.id}
          className="flex items-center gap-3 rounded-xl border border-orange-200 bg-white dark:border-stone-800 dark:bg-stone-900 px-4 py-3 shadow-sm"
        >
          <span className="w-6 text-center shrink-0">{MEDALS[i] ?? ""}</span>
          <span className="min-w-0 truncate flex-1 font-medium">{s.title}</span>
          <button
            onClick={() => handleVote(s.id)}
            disabled={votedIds.has(s.id)}
            className="inline-flex items-center gap-1 text-xs px-3 py-1.5 rounded-full border border-orange-300 text-orange-600 dark:text-orange-400 hover:bg-orange-100 dark:hover:bg-stone-800 transition-colors disabled:opacity-50 shrink-0"
          >
            👍 {s.like_count}
          </button>
        </li>
      ))}
    </ul>
  );
}
