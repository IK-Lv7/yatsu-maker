import Footer from "../components/Footer";

export default function PrivacyPage() {
  return (
    <div className="flex flex-col min-h-full">
      <header className="max-w-3xl mx-auto w-full px-4 pt-10 pb-6">
        <h1 className="text-2xl font-black text-orange-600 dark:text-orange-400">
          プライバシーポリシー
        </h1>
      </header>

      <main className="max-w-3xl mx-auto w-full px-4 flex-1 pb-10 text-sm leading-relaxed flex flex-col gap-4">
        <p>
          本サイト(以下「本サービス」)は、あるYouTubeチャンネルの動画タイトルの形式を学習した
          AIがタイトルを生成するファンメイドの非公式コンテンツです。特定の個人・団体を公式に
          代表するものではありません。
        </p>

        <section className="rounded-xl border border-orange-200 bg-white dark:border-stone-800 dark:bg-stone-900 p-4 shadow-sm">
          <h2 className="font-bold text-orange-600 dark:text-orange-400 mb-1">取得する情報</h2>
          <p>
            本サービスは、YouTube Data API v3を通じて、対象チャンネルの動画タイトル・
            投稿日時などの公開情報のみを取得します。視聴者のコメントや個人を特定する情報は
            取得・保存しません。
          </p>
        </section>

        <section className="rounded-xl border border-orange-200 bg-white dark:border-stone-800 dark:bg-stone-900 p-4 shadow-sm">
          <h2 className="font-bold text-orange-600 dark:text-orange-400 mb-1">
            YouTube API Servicesについて
          </h2>
          <p>
            本サービスはYouTube API Servicesを利用しています。利用にあたっては
            <a
              href="https://www.youtube.com/t/terms"
              target="_blank"
              rel="noopener noreferrer"
              className="underline hover:text-orange-600 dark:hover:text-orange-400"
            >
              YouTube利用規約
            </a>
            、および
            <a
              href="https://policies.google.com/privacy"
              target="_blank"
              rel="noopener noreferrer"
              className="underline hover:text-orange-600 dark:hover:text-orange-400"
            >
              Googleプライバシーポリシー
            </a>
            に従います。
          </p>
        </section>

        <section className="rounded-xl border border-orange-200 bg-white dark:border-stone-800 dark:bg-stone-900 p-4 shadow-sm">
          <h2 className="font-bold text-orange-600 dark:text-orange-400 mb-1">
            生成タイトルについて
          </h2>
          <p>
            本サービスで表示される生成タイトルはすべてAIによって生成された架空のもので、
            実在する動画タイトルではありません。
          </p>
        </section>
      </main>

      <Footer />
    </div>
  );
}
