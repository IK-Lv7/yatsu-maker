"use client";

export default function ShareButton({ title, date }: { title: string; date: string }) {
  const text = `AIが生成した「〜奴」タイトル(${date}):\n「${title}」`;
  const url =
    typeof window !== "undefined" ? window.location.href : "";
  const shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(
    text
  )}&url=${encodeURIComponent(url)}`;

  return (
    <a
      href={shareUrl}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-1 text-xs px-3 py-1.5 rounded-full border border-orange-300 text-orange-600 dark:text-orange-400 hover:bg-orange-100 dark:hover:bg-stone-800 transition-colors shrink-0"
    >
      Xでシェア
    </a>
  );
}
