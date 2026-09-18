from unittest.mock import patch

from ml.fetch.sync_videos import find_best_match, sync_results


def test_find_best_match_picks_highest_similarity():
    video = {
        "video_id": "v1",
        "title": "挨拶が長い奴",
        "published_at": "2026-01-01T09:00:00Z",
    }
    predictions = [
        {"id": 1, "title": "全く違う内容な奴"},
        {"id": 2, "title": "挨拶がやたら長い奴"},
    ]
    result = find_best_match(video, predictions)
    assert result is not None
    assert result["best_prediction_id"] == 2
    assert result["target_date"] == "2026-01-01"
    assert result["video_id"] == "v1"
    assert 0 < result["similarity"] <= 1


def test_find_best_match_no_predictions():
    video = {"video_id": "v1", "title": "な奴", "published_at": "2026-01-01T09:00:00Z"}
    assert find_best_match(video, []) is None


def test_sync_results_batches_by_date_not_per_video():
    """多数の動画があっても、日付ごとのクエリはN+1にならず1回にまとまる。"""
    videos = [
        {"video_id": f"v{i}", "title": "な奴", "published_at": "2026-01-01T09:00:00Z"}
        for i in range(50)
    ]

    with patch("ml.common.supabase_client.select", return_value=[]) as mock_select, patch(
        "ml.common.supabase_client.upsert"
    ) as mock_upsert:
        sync_results(videos)

    assert mock_select.call_count == 1
    mock_upsert.assert_called_once_with("results", [], on_conflict="target_date")
