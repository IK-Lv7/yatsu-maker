"""不適切表現フィルタ。

公開サービスのため、差別的・性的・特定個人を攻撃する表現をNGワードで除外する。
NGワードリストは最小限のプレースホルダーであり、運用開始前に必ずレビュー・拡充すること。
将来的に分類器(classifier)を組み込む場合は `classify_inappropriate` を差し替える。
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

DEFAULT_NG_WORDS_PATH = Path(__file__).parent / "ng_words.txt"


def load_ng_words(path: Path = DEFAULT_NG_WORDS_PATH) -> list[str]:
    if not path.exists():
        return []
    words = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            word = line.strip()
            if not word or word.startswith("#"):
                continue
            words.append(word)
    return words


def _normalize_for_match(text: str) -> str:
    return unicodedata.normalize("NFKC", text).lower()


def contains_ng_word(text: str, ng_words: list[str]) -> str | None:
    """マッチしたNGワードを返す。マッチしなければNone。"""
    normalized = _normalize_for_match(text)
    for word in ng_words:
        if _normalize_for_match(word) in normalized:
            return word
    return None


def classify_inappropriate(text: str) -> bool:
    """分類器による不適切判定のフック。未導入のため常にFalse(不適切でない)を返す。

    TODO: 差別的・性的・個人攻撃表現を検出する分類器をここに接続する。
    """
    return False


def is_appropriate(text: str, ng_words: list[str] | None = None) -> bool:
    words = ng_words if ng_words is not None else load_ng_words()
    if contains_ng_word(text, words) is not None:
        return False
    if classify_inappropriate(text):
        return False
    return True


_URL_RE = re.compile(r"https?://\S+")


def matches_format(
    title: str, suffix: str = "奴", min_len: int = 3, max_len: int = 40
) -> bool:
    """形式チェック: 「奴」で終わるか、長さが範囲内か、URLを含まないか。"""
    if not title.endswith(suffix):
        return False
    if not (min_len <= len(title) <= max_len):
        return False
    if _URL_RE.search(title):
        return False
    return True
