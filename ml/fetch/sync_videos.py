"""fetch_titles.py が取得したローカルJSONLをSupabaseに反映するCLI。

1. `videos` テーブルへ upsert する
2. 動画が投稿された日付(target_date)に予想(`predictions`)が存在すれば、
   最も似ていた予想を選んで類似度とともに `results` へ upsert する
   (AGENTS.md の「答え合わせジョブ」に対応)

使い方:
    python -m ml.fetch.sync_videos --input data/videos.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ml.generate.dedup import char_similarity


def load_videos(path: Path) -> list[dict]:
    videos = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            videos.append(json.loads(line))
    return videos


def find_best_match(video: dict, predictions: list[dict]) -> dict | None:
    """videoの投稿日にある予想の中から、最も似ていたものと類似度を返す。"""
    if not predictions:
        return None
    best = max(predictions, key=lambda p: char_similarity(video["title"], p["title"]))
    similarity = char_similarity(video["title"], best["title"])
    return {
        "target_date": video["published_at"][:10],
        "video_id": video["video_id"],
        "best_prediction_id": best["id"],
        "similarity": similarity,
    }


def sync_videos(videos: list[dict]) -> None:
    from ml.common.supabase_client import upsert

    upsert("videos", videos, on_conflict="video_id")


_DATE_BATCH_SIZE = 200  # PostgRESTのURL長を抑えるためのチャンクサイズ


def sync_results(videos: list[dict]) -> list[dict]:
    """各動画の投稿日にある予想と比較し、最も近かったものを results に保存する。"""
    from ml.common.supabase_client import select, upsert

    if not videos:
        return []

    target_dates = sorted({video["published_at"][:10] for video in videos})
    predictions_by_date: dict[str, list[dict]] = {date: [] for date in target_dates}
    for i in range(0, len(target_dates), _DATE_BATCH_SIZE):
        batch = target_dates[i : i + _DATE_BATCH_SIZE]
        rows = select("predictions", {"target_date": f"in.({','.join(batch)})"})
        for row in rows:
            predictions_by_date[row["target_date"]].append(row)

    result_rows: list[dict] = []
    for video in videos:
        target_date = video["published_at"][:10]
        match = find_best_match(video, predictions_by_date[target_date])
        if match:
            result_rows.append(match)
    upsert("results", result_rows, on_conflict="target_date")
    return result_rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="fetch_titles.py の出力JSONL")
    return parser


def main(argv: list[str] | None = None) -> int:
    from ml.common.supabase_client import select

    args = build_parser().parse_args(argv)
    videos = load_videos(args.input)

    # Supabase側が差分の正。既存動画は再処理しない
    existing_ids = {row["video_id"] for row in select("videos", {"select": "video_id"})}
    new_videos = [v for v in videos if v["video_id"] not in existing_ids]

    sync_videos(new_videos)
    results = sync_results(new_videos)
    print(f"{len(new_videos)} 件の新着動画をSupabaseに反映し、{len(results)} 件の答え合わせを保存しました")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
