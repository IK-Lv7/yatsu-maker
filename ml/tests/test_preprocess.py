from ml.common.schema import Video
from ml.preprocess.clean import clean_videos


def test_clean_videos_filters_non_na_yatsu():
    videos = [
        Video(video_id="1", title="【企画】早口言葉が下手な奴", published_at="2026-01-01T00:00:00Z"),
        Video(video_id="2", title="コラボ雑談回", published_at="2026-01-02T00:00:00Z"),
    ]
    cleaned = clean_videos(videos)
    assert len(cleaned) == 1
    assert cleaned[0].video_id == "1"
    assert cleaned[0].title == "早口言葉が下手な奴"


def test_clean_videos_filters_too_short():
    videos = [Video(video_id="1", title="な奴", published_at="2026-01-01T00:00:00Z")]
    assert clean_videos(videos) == []


def test_clean_videos_preserves_published_at():
    videos = [
        Video(video_id="1", title="即興コントが下手な奴", published_at="2026-03-01T12:00:00Z"),
    ]
    cleaned = clean_videos(videos)
    assert cleaned[0].published_at == "2026-03-01T12:00:00Z"


def test_clean_videos_accepts_any_yatsu_ending():
    """「な奴」に限らず、「〜する奴」「〜た奴」など「奴」で終わるものは全て対象。"""
    videos = [
        Video(video_id="1", title="路地裏に連れて行かれる奴", published_at="2026-01-01T00:00:00Z"),
        Video(video_id="2", title="全カットになった奴", published_at="2026-01-02T00:00:00Z"),
    ]
    cleaned = clean_videos(videos)
    assert {c.title for c in cleaned} == {"路地裏に連れて行かれる奴", "全カットになった奴"}
