"""尤度と多様性(MMR)に基づく候補のランキング。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ml.generate.dedup import char_similarity


@dataclass
class ScoredCandidate:
    title: str
    likelihood: float  # 生成時の対数尤度など、高いほど良いスコア


def _similarity(a: str, b: str) -> float:
    return char_similarity(a, b)


def mmr_rank(
    candidates: Sequence[ScoredCandidate],
    k: int,
    lambda_param: float = 0.7,
    similarity_fn=_similarity,
) -> list[ScoredCandidate]:
    """Maximal Marginal Relevance で上位k件を選ぶ。

    lambda_param: 1.0に近いほど尤度重視、0.0に近いほど多様性重視。
    """
    if k <= 0 or not candidates:
        return []

    remaining = list(candidates)
    selected: list[ScoredCandidate] = []

    max_likelihood = max((c.likelihood for c in remaining), default=1.0) or 1.0
    min_likelihood = min((c.likelihood for c in remaining), default=0.0)
    spread = max_likelihood - min_likelihood or 1.0

    def normalized_likelihood(c: ScoredCandidate) -> float:
        return (c.likelihood - min_likelihood) / spread

    while remaining and len(selected) < k:
        if not selected:
            best = max(remaining, key=normalized_likelihood)
        else:
            def mmr_score(c: ScoredCandidate) -> float:
                max_sim = max(similarity_fn(c.title, s.title) for s in selected)
                return lambda_param * normalized_likelihood(c) - (1 - lambda_param) * max_sim

            best = max(remaining, key=mmr_score)
        selected.append(best)
        remaining.remove(best)

    return selected
