import { supabasePublic } from "./supabase";

export type Submission = {
  id: number;
  title: string;
  like_count: number;
  created_at: string;
};

export async function listSubmissions(limit = 100): Promise<Submission[]> {
  const { data, error } = await supabasePublic()
    .from("submissions")
    .select("id,title,like_count,created_at")
    .order("like_count", { ascending: false })
    .order("created_at", { ascending: false })
    .limit(limit);
  if (error || !data) return [];
  return data;
}
