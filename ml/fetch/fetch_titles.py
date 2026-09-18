"""YouTubeチャンネルの動画タイトルを取得し、JSONLに差分保存するCLI。

使い方:
    python -m ml.fetch.fetch_titles --channel-id UCxxxx --output data/videos.jsonl

環境変数 YOUTUBE_API_KEY (または --api-key) が必要。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Iterator

import requests

from ml.common.schema import Video

API_BASE = "https://www.googleapis.com/youtube/v3"


class YouTubeApiError(RuntimeError):
    pass


def get_uploads_playlist_id(channel_id: str, api_key: str) -> str:
    resp = requests.get(
        f"{API_BASE}/channels",
        params={"part": "contentDetails", "id": channel_id, "key": api_key},
        timeout=30,
    )
    resp.raise_for_status()
    items = resp.json().get("items", [])
    if not items:
        raise YouTubeApiError(f"channel not found: {channel_id}")
    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]


def iter_playlist_videos(playlist_id: str, api_key: str) -> Iterator[Video]:
    page_token = None
    while True:
        params = {
            "part": "snippet",
            "playlistId": playlist_id,
            "maxResults": 50,
            "key": api_key,
        }
        if page_token:
            params["pageToken"] = page_token
        resp = requests.get(f"{API_BASE}/playlistItems", params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("items", []):
            snippet = item["snippet"]
            resource = snippet.get("resourceId", {})
            video_id = resource.get("videoId")
            if not video_id:
                continue
            yield Video(
                video_id=video_id,
                title=snippet["title"],
                published_at=snippet["publishedAt"],
            )
        page_token = data.get("nextPageToken")
        if not page_token:
            break


def load_existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    ids: set[str] = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ids.add(json.loads(line)["video_id"])
    return ids


def append_videos(path: Path, videos: list[Video]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for video in videos:
            f.write(json.dumps(video.to_dict(), ensure_ascii=False) + "\n")


def fetch_new_videos(channel_id: str, api_key: str, output_path: Path) -> list[Video]:
    existing_ids = load_existing_ids(output_path)
    playlist_id = get_uploads_playlist_id(channel_id, api_key)
    new_videos = [
        video for video in iter_playlist_videos(playlist_id, api_key)
        if video.video_id not in existing_ids
    ]
    append_videos(output_path, new_videos)
    return new_videos


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel-id", required=True, help="YouTubeチャンネルID")
    parser.add_argument(
        "--api-key", default=os.environ.get("YOUTUBE_API_KEY"),
        help="YouTube Data API v3 キー(未指定時は環境変数 YOUTUBE_API_KEY を使用)",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("data/videos.jsonl"),
        help="出力JSONLパス(既存分は差分スキップされる)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.api_key:
        print("エラー: --api-key または環境変数 YOUTUBE_API_KEY が必要です", file=sys.stderr)
        return 1
    new_videos = fetch_new_videos(args.channel_id, args.api_key, args.output)
    print(f"{len(new_videos)} 件の新着動画を {args.output} に保存しました")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
