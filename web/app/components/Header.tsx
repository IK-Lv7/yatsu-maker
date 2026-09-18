import Link from "next/link";

export default function Header() {
  return (
    <header className="sticky top-0 z-10 border-b border-orange-200/60 bg-orange-50/90 backdrop-blur dark:border-stone-800 dark:bg-stone-950/90">
      <div className="max-w-3xl mx-auto w-full px-4 py-3 flex flex-wrap items-center justify-between gap-x-3 gap-y-1">
        <Link
          href="/"
          className="font-bold text-orange-600 dark:text-orange-400 shrink-0 text-sm sm:text-base"
        >
          🎭 AI〜な奴メーカー
        </Link>
        <nav className="flex items-center gap-4 text-xs sm:text-sm shrink-0">
          <Link
            href="/archive"
            className="text-stone-600 hover:text-orange-600 dark:text-stone-400 dark:hover:text-orange-400 transition-colors whitespace-nowrap"
          >
            アーカイブ
          </Link>
          <Link
            href="/submissions"
            className="text-stone-600 hover:text-orange-600 dark:text-stone-400 dark:hover:text-orange-400 transition-colors whitespace-nowrap"
          >
            みんなの投稿
          </Link>
        </nav>
      </div>
    </header>
  );
}
