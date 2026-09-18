"""Supabase PostgREST への薄いラッパー。

supabase-py 等の重い依存を避け、requests で直接 REST API を叩く。
バッチジョブ(fetch/generate)は service role キーで書き込みを行う。
"""

from __future__ import annotations

import os
from typing import Any

import requests


class SupabaseConfigError(RuntimeError):
    pass


def _base_url() -> str:
    url = os.environ.get("SUPABASE_URL")
    if not url:
        raise SupabaseConfigError("環境変数 SUPABASE_URL が設定されていません")
    return url.rstrip("/")


def _service_role_key() -> str:
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not key:
        raise SupabaseConfigError("環境変数 SUPABASE_SERVICE_ROLE_KEY が設定されていません")
    return key


def _headers(key: str) -> dict[str, str]:
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


_PAGE_SIZE = 1000  # PostgREST(Supabase既定)の1リクエストあたりの応答上限に合わせる


def select(table: str, params: dict[str, str] | None = None) -> list[dict[str, Any]]:
    """service role キーで SELECT する。Rangeヘッダーでページネーションし全件取得。"""
    key = _service_role_key()
    rows: list[dict[str, Any]] = []
    offset = 0
    while True:
        headers = _headers(key)
        headers["Range"] = f"{offset}-{offset + _PAGE_SIZE - 1}"
        resp = requests.get(
            f"{_base_url()}/rest/v1/{table}",
            headers=headers,
            params=params or {},
            timeout=30,
        )
        resp.raise_for_status()
        page = resp.json()
        rows.extend(page)
        if len(page) < _PAGE_SIZE:
            break
        offset += _PAGE_SIZE
    return rows


def upsert(table: str, rows: list[dict[str, Any]], on_conflict: str) -> None:
    """rows を upsert する。空リストなら何もしない。"""
    if not rows:
        return
    key = _service_role_key()
    headers = _headers(key)
    headers["Prefer"] = "resolution=merge-duplicates"
    resp = requests.post(
        f"{_base_url()}/rest/v1/{table}",
        headers=headers,
        params={"on_conflict": on_conflict},
        json=rows,
        timeout=30,
    )
    resp.raise_for_status()
