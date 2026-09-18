"""動画タイトルのクリーニング・フィルタCLI。

「奴」で終わるタイトルのみを対象に、装飾除去・NFKC正規化を行い、
学習用JSONL(CleanedTitle)を出力する。

使い方:
    python -m ml.preprocess.clean --input data/videos.jsonl --output data/cleaned.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Iterator

from ml.common.schema import CleanedTitle, Video
from ml.common.text import ends_with_suffix, is_valid_length, normalize_title


def load_videos(path: Path) -> Iterator[Video]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield Video.from_dict(json.loads(line))


def clean_videos(videos: Iterable[Video]) -> list[CleanedTitle]:
    cleaned: list[CleanedTitle] = []
    for video in videos:
        title = normalize_title(video.title)
        if not ends_with_suffix(title):
            continue
        if not is_valid_length(title):
            continue
        cleaned.append(
            CleanedTitle(video_id=video.video_id, title=title, published_at=video.published_at)
        )
    return cleaned


def write_cleaned(path: Path, cleaned: list[CleanedTitle]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for item in cleaned:
            f.write(json.dumps(item.to_dict(), ensure_ascii=False) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="fetchで取得したJSONL")
    parser.add_argument("--output", type=Path, required=True, help="クリーニング後の出力JSONL")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    videos = list(load_videos(args.input))
    cleaned = clean_videos(videos)
    write_cleaned(args.output, cleaned)
    print(f"{len(videos)} 件中 {len(cleaned)} 件を「奴」タイトルとして抽出しました")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
