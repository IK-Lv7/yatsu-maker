import Footer from "../components/Footer";
import SubmissionForm from "../components/SubmissionForm";
import SubmissionList from "../components/SubmissionList";
import { listSubmissions } from "../lib/submissions";

export const dynamic = "force-dynamic";

export default async function SubmissionsPage() {
  const submissions = await listSubmissions();

  return (
    <div className="flex flex-col min-h-full">
      <header className="max-w-3xl mx-auto w-full px-4 pt-10 pb-6">
        <h1 className="text-2xl font-black text-orange-600 dark:text-orange-400">
          みんなの「〜奴」投稿
        </h1>
        <p className="mt-1 text-sm text-stone-500">
          自分で考えた「〜奴」タイトルを投稿して、いいねを集めよう。
        </p>
      </header>

      <main className="max-w-3xl mx-auto w-full px-4 flex-1 pb-10">
        <SubmissionForm />
        <SubmissionList submissions={submissions} />
      </main>

      <Footer />
    </div>
  );
}
