import Footer from "../components/Footer";
import { getPredictionsForDate, listPredictionDates } from "../lib/predictions";
import { getResultForDate } from "../lib/results";

export const dynamic = "force-dynamic";

export default async function ArchivePage() {
  const dates = await listPredictionDates();

  const rows = await Promise.all(
    dates.map(async (date) => {
      const predictions = await getPredictionsForDate(date);
      const result = await getResultForDate(date);
      return { date, predictions, result };
    })
  );

  return (
    <div className="flex flex-col min-h-full">
      <header className="max-w-3xl mx-auto w-full px-4 pt-10 pb-6">
        <h1 className="text-2xl font-black text-orange-600 dark:text-orange-400">
          生成アーカイブ
        </h1>
        <p className="mt-1 text-sm text-stone-500">過去に生成したタイトルの一覧です。</p>
      </header>

      <main className="max-w-3xl mx-auto w-full px-4 flex-1 flex flex-col gap-6 pb-10">
        {rows.length === 0 && (
          <p className="text-sm text-stone-500 rounded-xl border border-dashed border-orange-200 dark:border-stone-800 px-4 py-6 text-center">
            まだ生成データがありません。
          </p>
        )}
        {rows.map(({ date, predictions, result }) => (
          <section
            key={date}
            className="rounded-xl border border-orange-200 bg-white dark:border-stone-800 dark:bg-stone-900 p-4 shadow-sm"
          >
            <h2 className="font-bold text-orange-600 dark:text-orange-400 mb-3">{date}</h2>

            <ul className="flex flex-col gap-1 mb-3">
              {predictions?.map((p) => (
                <li
                  key={p.rank}
                  className={`text-sm ${
                    result?.bestPredictionTitle === p.title
                      ? "font-bold text-orange-700 dark:text-orange-400"
                      : "text-stone-700 dark:text-stone-300"
                  }`}
                >
                  {p.title}
                </li>
              ))}
            </ul>

            {result && (
              <p className="text-xs text-stone-500 border-t border-orange-100 dark:border-stone-800 pt-2">
                🎬 おまけ: 実際のタイトルは「{result.videoTitle}」でした
                (一番近かった生成タイトルとの類似度 {Math.round(result.similarity * 100)}%)
              </p>
            )}
          </section>
        ))}
      </main>

      <Footer />
    </div>
  );
}
