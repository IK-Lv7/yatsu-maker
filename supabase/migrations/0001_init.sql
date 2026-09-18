-- 初期スキーマ: 動画・AI生成タイトル・答え合わせ・ユーザー投稿・いいね

create table if not exists videos (
  video_id text primary key,
  title text not null,
  published_at timestamptz not null
);

create table if not exists predictions (
  id bigint generated always as identity primary key,
  target_date date not null,
  title text not null,
  rank int not null,
  score double precision not null,
  model_version text not null,
  created_at timestamptz not null default now(),
  unique (target_date, rank)
);

create index if not exists predictions_target_date_idx on predictions (target_date);

create table if not exists results (
  target_date date primary key,
  video_id text not null references videos (video_id),
  best_prediction_id bigint references predictions (id),
  similarity double precision not null
);

create table if not exists submissions (
  id bigint generated always as identity primary key,
  title text not null check (title ~ '奴$') check (char_length(title) between 3 and 40),
  like_count int not null default 0,
  created_at timestamptz not null default now()
);

create index if not exists submissions_like_count_idx on submissions (like_count desc);

create table if not exists votes (
  id bigint generated always as identity primary key,
  submission_id bigint not null references submissions (id) on delete cascade,
  voter_id text not null,
  created_at timestamptz not null default now(),
  unique (submission_id, voter_id)
);

-- votes の増減に合わせて submissions.like_count を同期する
create or replace function sync_submission_like_count()
returns trigger
language plpgsql
as $$
begin
  if tg_op = 'INSERT' then
    update submissions set like_count = like_count + 1 where id = new.submission_id;
    return new;
  elsif tg_op = 'DELETE' then
    update submissions set like_count = like_count - 1 where id = old.submission_id;
    return old;
  end if;
  return null;
end;
$$;

create trigger votes_sync_like_count
after insert or delete on votes
for each row execute function sync_submission_like_count();

-- RLS: 公開読み取りは videos / predictions / results / submissions のみ。
-- submissions への insert とすべての votes 操作は、Route Handler がサーバー側で
-- 形式チェック・NGワードフィルタを通した上で service role キー(RLSをバイパスする)
-- で行うため、anon 向けの insert ポリシーは意図的に用意しない。

alter table videos enable row level security;
alter table predictions enable row level security;
alter table results enable row level security;
alter table submissions enable row level security;
alter table votes enable row level security;

create policy "public read videos" on videos for select using (true);
create policy "public read predictions" on predictions for select using (true);
create policy "public read results" on results for select using (true);
create policy "public read submissions" on submissions for select using (true);
