import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { supabaseAdmin } from "@/app/lib/supabase";

const VOTER_COOKIE = "voter_id";

export async function POST(_request: Request, ctx: RouteContext<"/api/submissions/[id]/vote">) {
  const { id } = await ctx.params;
  const submissionId = Number(id);
  if (!Number.isInteger(submissionId)) {
    return NextResponse.json({ error: "invalid_id" }, { status: 400 });
  }

  const cookieStore = await cookies();
  let voterId = cookieStore.get(VOTER_COOKIE)?.value;
  if (!voterId) {
    voterId = crypto.randomUUID();
    cookieStore.set(VOTER_COOKIE, voterId, {
      httpOnly: true,
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 365,
    });
  }

  const { error } = await supabaseAdmin()
    .from("votes")
    .insert({ submission_id: submissionId, voter_id: voterId });

  if (error) {
    // unique制約違反(23505) = 既にいいね済み。エラーではなく現状として扱う
    if (error.code === "23505") {
      return NextResponse.json({ already_voted: true });
    }
    return NextResponse.json({ error: "vote_failed" }, { status: 500 });
  }

  return NextResponse.json({ already_voted: false });
}
