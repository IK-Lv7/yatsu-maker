import Link from "next/link";
import Footer from "./components/Footer";
import SubmissionForm from "./components/SubmissionForm";
import SubmissionList from "./components/SubmissionList";
import { getLatestPredictions, listPredictionDates } from "./lib/predictions";
import { getResultForDate } from "./lib/results";
import { listSubmissions } from "./lib/submissions";

// ビルドを経由せず更新されるSupabaseの内容を毎回反映するため動的レンダリングにする
export const dynamic = "force-dynamic";

function formatDate(date: string): string {
  const d = new Date(`${date}T00:00:00+09:00`);
  return d.toLocaleDateString("ja-JP", {
    year: "numeric",
    month: "long",
    day: "numeric",
    weekday: "short",
  });
}

export default async function HomePage() {
  const latest = await getLatestPredictions();
  const dates = await listPredictionDates();
  const yesterdayDate = dates[1] ?? null;
  const yesterdayResult = yesterdayDate ? await getResultForDate(yesterdayDate) : null;
  const topSubmissions = (await listSubmissions()).slice(0, 5);

  return (
    <div className="flex flex-col min-h-full">
      <section className="border-b border-orange-200/60 dark:border-stone-800 bg-gradient-to-b from-orange-100 to-orange-50 dark:from-stone-900 dark:to-stone-950">
        <div className="max-w-3xl mx-auto w-full px-4 py-12 text-center">
          <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-orange-600 dark:text-orange-400">
            AI〜な奴メーカー
          </h1>
          <p className="mt-3 text-sm sm:text-base text-stone-600 dark:text-stone-300 max-w-xl mx-auto">
            あなたが考えた「〜奴」タイトルを投稿していいねを集めよう。
            AIが生成したタイトルも毎日お届けします。
          </p>
        </div>
      </section>

      <main className="max-w-3xl mx-auto w-full px-4 flex-1 py-8">
        <section>
          <h2 className="text-base font-bold mb-3 flex items-center gap-2 text-stone-600 dark:text-stone-400">
            <span className="inline-flex items-center justify-center size-6 rounded-full bg-stone-400 text-white text-xs">
              🎤
            </span>
            {latest ? `${formatDate(latest.date)} のAI生成タイトル` : "AI生成タイトル"}
          </h2>
          {latest ? (
            <ul className="flex flex-col gap-2">
              {latest.predictions.map((p) => (
                <li
                  key={p.rank}
                  className="rounded-xl border border-orange-200 bg-white px-4 py-3 shadow-sm transition-shadow hover:shadow-md dark:border-stone-800 dark:bg-stone-900"
                >
                  <span className="truncate font-medium">{p.title}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-stone-500 rounded-xl border border-dashed border-orange-200 dark:border-stone-800 px-4 py-6 text-center">
              まだ生成データがありません。バッチの実行をお待ちください。
            </p>
          )}
          <div className="mt-3 text-right">
            <Link
              href="/archive"
              className="text-sm text-stone-500 underline hover:text-orange-600 dark:hover:text-orange-400 hover:no-underline"
            >
              過去の生成タイトルを見る →
            </Link>
          </div>
        </section>

        <section className="mt-12">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <span className="inline-flex items-center justify-center size-8 rounded-full bg-orange-500 text-white text-base">
              📝
            </span>
            みんなの「〜奴」投稿
          </h2>
          <SubmissionForm />
          <SubmissionList submissions={topSubmissions} />
          <div className="mt-3 text-right">
            <Link
              href="/submissions"
              className="text-sm font-medium text-orange-600 dark:text-orange-400 underline hover:no-underline"
            >
              投稿ランキングをもっと見る →
            </Link>
          </div>
        </section>

        {yesterdayResult && (
          <section className="mt-10 rounded-xl border border-orange-200 bg-orange-100/60 dark:border-stone-800 dark:bg-stone-900 px-4 py-4 text-sm text-stone-600 dark:text-stone-300">
            <p className="font-semibold text-orange-700 dark:text-orange-400 mb-2">
              🎬 おまけ: {formatDate(yesterdayResult.targetDate)}の答え合わせ
            </p>
            <p className="mb-1">
              実際に投稿されたタイトルは「{yesterdayResult.videoTitle}」でした。
            </p>
            <p>
              AIの生成タイトルの中で一番近かったのは「{yesterdayResult.bestPredictionTitle}」
              (類似度 {Math.round(yesterdayResult.similarity * 100)}%)でした。
            </p>
          </section>
        )}
      </main>

      <Footer />
    </div>
  );
}
