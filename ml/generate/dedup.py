"""既存タイトルとの重複除去。

完全一致に加え、テキスト類似度が閾値以上のものを「丸暗記」とみなして除外する。
埋め込みモデル(sentence-transformers等)が利用可能ならそれを使い、
利用できない環境では difflib による文字列類似度にフォールバックする。
"""

from __future__ import annotations

import difflib
from typing import Callable, Sequence

EmbedFn = Callable[[Sequence[str]], Sequence[Sequence[float]]]


def is_exact_duplicate(title: str, existing_titles: set[str]) -> bool:
    return title in existing_titles


def char_similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


def is_near_duplicate_lexical(
    title: str, existing_titles: Sequence[str], threshold: float = 0.9
) -> bool:
    return any(char_similarity(title, existing) >= threshold for existing in existing_titles)


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def is_near_duplicate_embedding(
    title: str,
    existing_titles: Sequence[str],
    embed_fn: EmbedFn,
    threshold: float = 0.92,
) -> bool:
    if not existing_titles:
        return False
    vectors = embed_fn([title, *existing_titles])
    title_vec, existing_vecs = vectors[0], vectors[1:]
    return any(cosine_similarity(title_vec, vec) >= threshold for vec in existing_vecs)


def filter_duplicates(
    candidates: Sequence[str],
    existing_titles: Sequence[str],
    embed_fn: EmbedFn | None = None,
    lexical_threshold: float = 0.9,
    embedding_threshold: float = 0.92,
) -> list[str]:
    """完全一致・(埋め込みor文字列)類似の重複を除いた候補リストを返す。"""
    existing_set = set(existing_titles)
    result: list[str] = []
    for title in candidates:
        if is_exact_duplicate(title, existing_set):
            continue
        if embed_fn is not None:
            if is_near_duplicate_embedding(title, existing_titles, embed_fn, embedding_threshold):
                continue
        else:
            if is_near_duplicate_lexical(title, existing_titles, lexical_threshold):
                continue
        result.append(title)
    return result
