import Link from "next/link";

export default function Footer() {
  return (
    <footer className="mt-auto border-t border-orange-200/60 dark:border-stone-800 py-6 px-4 text-xs text-stone-500 dark:text-stone-400">
      <div className="max-w-3xl mx-auto flex flex-col gap-2">
        <p>
          本サイトはファンメイドの非公式コンテンツであり、特定の個人・団体を公式に代表するものではありません。
          表示されるタイトルはすべてAIによって生成された架空のものであり、実在する動画タイトルではありません。
        </p>
        <p>本サービスはYouTube API Servicesを利用しています。</p>
        <div className="flex gap-4">
          <Link href="/privacy" className="underline hover:text-orange-600 dark:hover:text-orange-400">
            プライバシーポリシー
          </Link>
        </div>
      </div>
    </footer>
  );
}
