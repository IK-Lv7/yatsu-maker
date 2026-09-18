import { supabasePublic } from "./supabase";

export type Video = {
  video_id: string;
  title: string;
  published_at: string; // ISO 8601
};

export async function getVideoByDate(targetDate: string): Promise<Video | null> {
  const { data, error } = await supabasePublic()
    .from("videos")
    .select("video_id,title,published_at")
    .gte("published_at", `${targetDate}T00:00:00Z`)
    .lt("published_at", `${targetDate}T23:59:59.999Z`)
    .limit(1)
    .maybeSingle();
  if (error) return null;
  return data;
}
