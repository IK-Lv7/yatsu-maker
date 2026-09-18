# AGENTS.md

## プロジェクト概要

対象チャンネル(YouTube)の過去の動画タイトル(「〜奴」形式)を学習した AI が、毎日それらしいタイトルを生成して公開する Web サービス。「予想を当てるゲーム」ではなく「AI生成タイトルを眺めて楽しむ・シェアするツール」として位置づける。特定の個人・団体名はサイト上・リポジトリ上ともに出さない方針。

**サイトの主役はユーザー投稿(「みんなの投稿」)**。AI生成タイトルは量より質で厳選して見せる、いわば「呼び水」的な位置づけ。

- コア体験: 自分で考えた「〜奴」タイトルを投稿していいねを集める → AIが生成した厳選タイトルも見る → 気に入ったものをシェアする(実際の投稿との答え合わせは「おまけ」の位置づけ)
- 生成エンジン: 小型日本語 LM を LoRA でファインチューニングしたモデル
- 特定の個人・団体を公式に代表するものではないことを常に明示する

## 基本方針

- **推論はリアルタイムで行わない**。1 日 1 回のバッチで生成タイトルを事前生成し、保存して配信する(GPU 常駐コストを避けるため)
- 生成タイトルの公開は、その日の動画投稿より前に行う
- 研究的な評価よりも、「毎日見に来たくなるか」「シェアしたくなるか」を優先する

## 技術スタック

| 役割 | 採用技術 |
|---|---|
| フロントエンド | Next.js (App Router) + TypeScript + Tailwind CSS |
| ホスティング | Vercel |
| DB / 認証 | Supabase (Postgres, Auth) |
| 定期実行 | GitHub Actions (schedule) |
| 学習 | Python, transformers, peft(ローカル GPU または Colab) |
| 推論バッチ | Python。サーバーレス GPU(Modal 等)または CPU 実行 |
| タイトル取得 | YouTube Data API v3 |

## ディレクトリ構成

```
.
├── AGENTS.md
├── web/                # Next.js アプリ
├── ml/
│   ├── fetch/          # タイトル取得
│   ├── preprocess/     # クリーニング・フィルタ
│   ├── train/          # LoRA 学習
│   ├── generate/       # 生成・後処理・ランキング
│   └── configs/        # YAML 設定
├── supabase/
│   └── migrations/     # スキーマ定義
└── .github/workflows/  # 日次バッチ
```

## 画面・機能

### MVP
- **トップ**: メインは投稿フォーム+投稿ランキングの上位抜粋(「みんなの投稿」)。
  その下に、今日のAI生成タイトル(既定 5 件、量より質で厳選)を控えめに表示する。
  昨日の答え合わせ(実タイトルと最も近かった生成タイトル、類似度スコア)は最下部に「おまけ」として表示する
- **投稿・いいね**(`/submissions`): ユーザーが自分で考えた「〜奴」タイトルを投稿し、匿名(Cookieベースの識別子)でいいねしてランキングできる。
  投稿は Route Handler 経由でサーバー側の形式チェック・NGワードフィルタを通してから保存する。トップページにも上位抜粋を表示する
- **アーカイブ**: 日付ごとの生成タイトルと実タイトルの一覧
- **シェア**: タイトルごとに X 共有ボタン。OGP 画像を動的生成(`next/og`、未実装 / TODO)
- **フッター**: 非公式である旨、プライバシーポリシー、YouTube API 利用の表示

### MVP 後
- Supabase Auth でのログインに切り替え、いいねの不正対策を強化する
- 「神生成」「神投稿」(類似度・いいね数が高かったもの)の殿堂ページ

## データベース(Supabase)

AI生成タイトルの配信、ユーザー投稿・いいね機能まで含めてSupabaseに一元化する。

- `videos`: `video_id`, `title`, `published_at`
- `predictions`: `id`, `target_date`, `title`, `rank`, `score`, `model_version`, `created_at`
- `results`: `target_date`, `video_id`, `best_prediction_id`, `similarity`
- `submissions`: `id`, `title`, `like_count`, `created_at`。ユーザーが投稿する「〜奴」タイトル
- `votes`: `id`, `submission_id`, `voter_id`(匿名識別子、Cookie等), `created_at`。
  `(submission_id, voter_id)` に一意制約を付け、同一ブラウザからの多重いいねを防ぐ
- RLS を有効にする
  - 公開読み取り: `predictions`, `results`, `videos`, `submissions`
  - `submissions` への書き込み・`votes` への書き込みは、Next.js の Route Handler
    経由(サーバー側で形式チェック・NGワードフィルタを通してから service role キーで insert)。
    クライアントから直接 insert はさせない
  - `videos` / `predictions` / `results` への書き込みはバッチ用の service role キーのみ

## バッチ運用

推論用GPUを常時確保するコストを避けるため、学習だけ手動、それ以外はできるだけ
GitHub Actionsのホスト型ランナー(無料・無制限)で完結させる。学習済みLoRAアダプタは
数MB程度と小さいため、リポジトリに直接コミットしてホスト型ランナーから参照する。

1. **タイトル取得ジョブ**(GitHub Actions / ホスト型ランナー、月次)
   - `ml.fetch.fetch_titles` で新着タイトルを差分取得し、`ml.preprocess.clean` でクリーニングして
     `data/videos.jsonl` / `data/cleaned.jsonl` をリポジトリにコミットする(`.github/workflows/fetch.yml`)
2. **学習**(手動、月1回程度を目安にデスクトップGPUで実行)
   - `python -m ml.train.train_lora --config ml/configs/train_default.yaml`
   - 出力先(`output_dir`、既定: `models/lora-latest`)はリポジトリ内の固定パス。
     学習後に `git add models/lora-latest && git commit && git push` して
     GitHub Actionsから参照できるようにする(中間チェックポイントはコミット不要)
   - リリース前の品質確認として、直近のタイトルを除いて学習し、類似度が既存モデルより下がらないことを確かめる
3. **予想ジョブ**(GitHub Actions / ホスト型ランナー、日次、投稿より十分前)
   - N 件(既定 100)生成 → 後処理 → 上位 K 件(既定 10)を `data/predictions/YYYY-MM-DD.jsonl` にコミット
     (`.github/workflows/generate.yml`)。CPU推論のため生成に数十分かかる想定だが、
     パブリックリポジトリのActionsは時間無制限(1ジョブ6時間以内)なので許容する
4. **答え合わせジョブ**(未実装 / TODO): 実タイトルと予想の類似度を計算し結果を保存する処理
5. 失敗時は通知(Discord Webhook 等)し、前日のモデルで再試行する(未実装 / TODO)

## 予想エンジン

### データ
- 「奴」で終わるタイトルのみを学習対象とする(「〜な奴」「〜する奴」「〜た奴」など語尾は問わない)
- 【】、#タグ、シリーズ名などの装飾を除去し、NFKC で正規化する
- 投稿日を保持する

### 学習
- 1〜3B 級の日本語 LM(llm-jp-3、sarashina2.2 など)に LoRA を適用する
- タイトル全体を学習データとして causal LM を学習する(語尾は「〜な奴」「〜する奴」等さまざまなため、固定接尾辞はプロンプトに置かず、生成後の形式チェックで「奴」で終わっているかを確認する)
- 新着データを加えて定期的に再学習する(既定: 月 1 回)。`model_version` を記録する
- リリース前の品質確認として、直近のタイトルを除いて学習し、類似度が既存モデルより下がらないことを確かめる

### 生成と後処理
1. 形式チェック: 「奴」で終わるか、長さが範囲内か
2. 既存タイトルとの重複除去: 完全一致、および埋め込みの類似度が閾値以上のもの(丸暗記を「予想」として出さない)
3. **不適切表現フィルタ**: 差別的・性的・特定個人を攻撃する表現を NG ワードと分類器で除外する。公開サービスなので必須
4. ランキング: 尤度と多様性(MMR 等)で上位 K 件を選ぶ

## 法務・規約

- 非公式であることを全ページに明示する。公式ロゴ、サムネイル画像、動画の埋め込み以外での映像利用はしない
- チャンネル名や芸人名の使い方、収益化(広告など)を行う場合の可否は、公開前に確認する
- YouTube API Services の利用規約・Developer Policies に従う。特に API データの保存期間と更新の要件、プライバシーポリシーの設置を確認する
- 視聴者コメントは表示・保存しない
- 生成タイトルは AI による架空のものであることを明示する

## 開発ルール

- 型を付ける(TypeScript strict、Python は型ヒント)
- 秘密情報(YouTube API キー、Supabase service role キー)は環境変数で管理し、コミットしない。フロントに service role キーを渡さない
- ML の各ステップは CLI として単独実行できるようにする
- 前処理、重複除去、不適切表現フィルタにはユニットテストを書く
- スキーマ変更は必ず `supabase/migrations/` のマイグレーションで行う
