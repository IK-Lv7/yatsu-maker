from unittest.mock import MagicMock, patch

import pytest

from ml.common.supabase_client import _PAGE_SIZE, SupabaseConfigError, select, upsert


def test_select_requires_supabase_url(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "key")
    with pytest.raises(SupabaseConfigError):
        select("videos")


def test_select_requires_service_role_key(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    with pytest.raises(SupabaseConfigError):
        select("videos")


def test_select_builds_request(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "secret-key")

    mock_response = MagicMock()
    mock_response.json.return_value = [{"video_id": "v1"}]
    with patch("ml.common.supabase_client.requests.get", return_value=mock_response) as mock_get:
        result = select("videos", {"select": "video_id"})

    assert result == [{"video_id": "v1"}]
    args, kwargs = mock_get.call_args
    assert args[0] == "https://example.supabase.co/rest/v1/videos"
    assert kwargs["headers"]["apikey"] == "secret-key"
    assert kwargs["headers"]["Authorization"] == "Bearer secret-key"
    assert kwargs["params"] == {"select": "video_id"}
    assert kwargs["headers"]["Range"] == f"0-{_PAGE_SIZE - 1}"


def test_select_trims_supabase_env_values(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", " https://example.supabase.co/ \n")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", " secret-key\n")

    mock_response = MagicMock()
    mock_response.json.return_value = [{"video_id": "v1"}]
    with patch("ml.common.supabase_client.requests.get", return_value=mock_response) as mock_get:
        select("videos", {"select": "video_id"})

    args, kwargs = mock_get.call_args
    assert args[0] == "https://example.supabase.co/rest/v1/videos"
    assert kwargs["headers"]["apikey"] == "secret-key"


def test_select_paginates_full_pages(monkeypatch):
    """PostgRESTの応答上限(1ページ分ちょうど)を超えるデータは複数リクエストで取得する。"""
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "secret-key")

    full_page = [{"video_id": f"v{i}"} for i in range(_PAGE_SIZE)]
    last_page = [{"video_id": "v-last"}]

    responses = []
    for page in (full_page, last_page):
        resp = MagicMock()
        resp.json.return_value = page
        responses.append(resp)

    with patch("ml.common.supabase_client.requests.get", side_effect=responses) as mock_get:
        result = select("videos")

    assert len(result) == _PAGE_SIZE + 1
    assert mock_get.call_count == 2
    first_range = mock_get.call_args_list[0].kwargs["headers"]["Range"]
    second_range = mock_get.call_args_list[1].kwargs["headers"]["Range"]
    assert first_range == f"0-{_PAGE_SIZE - 1}"
    assert second_range == f"{_PAGE_SIZE}-{2 * _PAGE_SIZE - 1}"


def test_upsert_skips_empty_rows(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "secret-key")
    with patch("ml.common.supabase_client.requests.post") as mock_post:
        upsert("videos", [], on_conflict="video_id")
    mock_post.assert_not_called()


def test_upsert_sends_merge_duplicates_header(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "secret-key")

    mock_response = MagicMock()
    with patch("ml.common.supabase_client.requests.post", return_value=mock_response) as mock_post:
        upsert("videos", [{"video_id": "v1"}], on_conflict="video_id")

    args, kwargs = mock_post.call_args
    assert args[0] == "https://example.supabase.co/rest/v1/videos"
    assert kwargs["headers"]["Prefer"] == "resolution=merge-duplicates"
    assert kwargs["params"] == {"on_conflict": "video_id"}
    assert kwargs["json"] == [{"video_id": "v1"}]
    mock_response.raise_for_status.assert_called_once()
