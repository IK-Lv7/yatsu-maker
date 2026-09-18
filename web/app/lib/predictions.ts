import { supabasePublic } from "./supabase";

export type Prediction = {
  title: string;
  rank: number;
  score: number;
};

export type PredictionSet = {
  date: string; // YYYY-MM-DD
  predictions: Prediction[];
};

export async function listPredictionDates(): Promise<string[]> {
  const { data, error } = await supabasePublic()
    .from("predictions")
    .select("target_date")
    .order("target_date", { ascending: false });
  if (error || !data) return [];
  return [...new Set(data.map((row) => row.target_date as string))];
}

export async function getPredictionsForDate(
  date: string
): Promise<Prediction[] | null> {
  const { data, error } = await supabasePublic()
    .from("predictions")
    .select("title,rank,score")
    .eq("target_date", date)
    .order("rank", { ascending: true });
  if (error || !data || data.length === 0) return null;
  return data;
}

export async function getLatestPredictions(): Promise<PredictionSet | null> {
  const dates = await listPredictionDates();
  if (dates.length === 0) return null;
  const [latest] = dates;
  const predictions = await getPredictionsForDate(latest);
  if (!predictions) return null;
  return { date: latest, predictions };
}
