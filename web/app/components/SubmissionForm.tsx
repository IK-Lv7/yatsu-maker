"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function SubmissionForm() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("submitting");
    setErrorMessage(null);

    const res = await fetch("/api/submissions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });

    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      const message =
        body.error === "invalid_format"
          ? "「〜奴」で終わる3〜40文字のタイトルにしてください"
          : body.error === "inappropriate"
            ? "不適切な表現が含まれています"
            : "投稿に失敗しました";
      setErrorMessage(message);
      setStatus("error");
      return;
    }

    setTitle("");
    setStatus("idle");
    router.refresh();
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-2 mb-8 rounded-xl border border-orange-200 bg-white dark:border-stone-800 dark:bg-stone-900 p-4 shadow-sm"
    >
      <label htmlFor="title" className="text-sm font-medium text-stone-600 dark:text-stone-300">
        あなたが考えた「〜奴」タイトルを投稿してみましょう
      </label>
      <div className="flex gap-2">
        <input
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="例: 早口言葉が異常に得意な奴"
          maxLength={40}
          required
          className="flex-1 rounded-lg border border-orange-200 dark:border-stone-700 bg-orange-50/50 dark:bg-stone-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
        />
        <button
          type="submit"
          disabled={status === "submitting"}
          className="rounded-lg bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 text-sm font-medium transition-colors disabled:opacity-50"
        >
          投稿
        </button>
      </div>
      {errorMessage && <p className="text-xs text-red-600">{errorMessage}</p>}
    </form>
  );
}
