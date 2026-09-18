import json
from pathlib import Path

from ml.common.schema import Video
from ml.fetch.fetch_titles import append_videos, load_existing_ids


def test_load_existing_ids_missing_file(tmp_path: Path):
    assert load_existing_ids(tmp_path / "nope.jsonl") == set()


def test_append_and_load_existing_ids(tmp_path: Path):
    path = tmp_path / "videos.jsonl"
    videos = [
        Video(video_id="a1", title="タイトルな奴", published_at="2026-01-01T00:00:00Z"),
        Video(video_id="a2", title="別のタイトルな奴", published_at="2026-01-02T00:00:00Z"),
    ]
    append_videos(path, videos)

    assert load_existing_ids(path) == {"a1", "a2"}

    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert json.loads(lines[0])["video_id"] == "a1"


def test_append_videos_is_additive(tmp_path: Path):
    path = tmp_path / "videos.jsonl"
    append_videos(path, [Video(video_id="a1", title="タイトルな奴", published_at="2026-01-01T00:00:00Z")])
    append_videos(path, [Video(video_id="a2", title="別のな奴", published_at="2026-01-02T00:00:00Z")])
    assert load_existing_ids(path) == {"a1", "a2"}
