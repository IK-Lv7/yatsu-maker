import { supabasePublic } from "./supabase";

export type ResultWithMatch = {
  targetDate: string;
  videoTitle: string;
  bestPredictionTitle: string;
  similarity: number;
};

/** バッチジョブ(ml.fetch.sync_videos)が計算済みの答え合わせ結果を取得する。 */
export async function getResultForDate(date: string): Promise<ResultWithMatch | null> {
  const { data: result, error } = await supabasePublic()
    .from("results")
    .select("target_date,similarity,video_id,best_prediction_id")
    .eq("target_date", date)
    .maybeSingle();
  if (error || !result || !result.best_prediction_id) return null;

  const [{ data: video }, { data: prediction }] = await Promise.all([
    supabasePublic()
      .from("videos")
      .select("title")
      .eq("video_id", result.video_id)
      .maybeSingle(),
    supabasePublic()
      .from("predictions")
      .select("title")
      .eq("id", result.best_prediction_id)
      .maybeSingle(),
  ]);
  if (!video || !prediction) return null;

  return {
    targetDate: result.target_date,
    videoTitle: video.title,
    bestPredictionTitle: prediction.title,
    similarity: result.similarity,
  };
}
