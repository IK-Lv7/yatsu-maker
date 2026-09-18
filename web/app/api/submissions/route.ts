import { NextResponse } from "next/server";
import { supabaseAdmin } from "@/app/lib/supabase";
import { listSubmissions } from "@/app/lib/submissions";
import { isAppropriate, matchesFormat } from "@/app/lib/moderation";

export async function GET() {
  const submissions = await listSubmissions();
  return NextResponse.json({ submissions });
}

export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "invalid_json" }, { status: 400 });
  }

  const title = typeof body === "object" && body !== null && "title" in body
    ? String((body as { title: unknown }).title).trim()
    : "";

  if (!matchesFormat(title)) {
    return NextResponse.json({ error: "invalid_format" }, { status: 400 });
  }
  if (!isAppropriate(title)) {
    return NextResponse.json({ error: "inappropriate" }, { status: 400 });
  }

  const { data, error } = await supabaseAdmin()
    .from("submissions")
    .insert({ title })
    .select("id,title,like_count,created_at")
    .single();

  if (error) {
    return NextResponse.json({ error: "insert_failed" }, { status: 500 });
  }

  return NextResponse.json({ submission: data }, { status: 201 });
}
