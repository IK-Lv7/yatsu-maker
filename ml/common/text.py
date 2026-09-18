"""Title text normalization shared by preprocess and generate steps."""

from __future__ import annotations

import os
import re
import unicodedata

SUFFIX = "奴"

_KAGI_RE = re.compile(r"『(.*)』")  # 貪欲マッチで入れ子『』にも対応
_BRACKET_RE = re.compile(r"【[^】]*】")  # シリーズ・企画名タグ
_HASHTAG_RE = re.compile(r"#\S+")
_TRAILING_NOISE_RE = re.compile(r"[|｜/／].*$")  # 区切り記号以降のチャンネル名等
_TRAILING_TILDE_RE = re.compile(r"[〜~～][^〜~～]*[〜~～]\s*$")  # 末尾の〜サブタイトル〜
_TRAILING_PART_RE = re.compile(r"\s*パート\s*[0-9０-９]+\s*$")
_WHITESPACE_RE = re.compile(r"\s+")

def _load_default_noise_strings() -> tuple[str, ...]:
    """実チャンネル名などの固有文字列はコードに書かず環境変数から読む(区切り文字: |)。"""
    raw = os.environ.get("TITLE_NOISE_STRINGS", "")
    return tuple(s for s in raw.split("|") if s)


DEFAULT_NOISE_STRINGS = _load_default_noise_strings()


def normalize_title(title: str, noise_strings: tuple[str, ...] = DEFAULT_NOISE_STRINGS) -> str:
    """NFKCで正規化し、装飾(括弧・ハッシュタグ・チャンネル名等)を除去する。"""
    text = unicodedata.normalize("NFKC", title)
    kagi_match = _KAGI_RE.search(text)
    if kagi_match:
        text = kagi_match.group(1)
    text = _BRACKET_RE.sub("", text)
    text = _TRAILING_TILDE_RE.sub("", text)
    text = _TRAILING_PART_RE.sub("", text)
    text = _HASHTAG_RE.sub("", text)
    text = _TRAILING_NOISE_RE.sub("", text)
    for noise in noise_strings:
        text = text.replace(noise, "")
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


def ends_with_suffix(title: str, suffix: str = SUFFIX) -> bool:
    return title.endswith(suffix)


def strip_suffix(title: str, suffix: str = SUFFIX) -> str:
    if title.endswith(suffix):
        return title[: -len(suffix)]
    return title


def is_valid_length(title: str, min_len: int = 3, max_len: int = 40) -> bool:
    return min_len <= len(title) <= max_len
