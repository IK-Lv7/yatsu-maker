import { createClient } from "@supabase/supabase-js";

/** 公開読み取り専用のクライアント(publishable key、RLSの"public read"ポリシーの範囲内)。 */
export function supabasePublic() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!
  );
}

/** secret(service role)キーを使うサーバー専用クライアント。Route Handler 以外では使わない。 */
export function supabaseAdmin() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );
}
