from ml.generate.rank import ScoredCandidate, mmr_rank


def test_mmr_rank_picks_top_k():
    candidates = [
        ScoredCandidate(title="挨拶が長い奴", likelihood=0.9),
        ScoredCandidate(title="挨拶がとても長い奴", likelihood=0.8),
        ScoredCandidate(title="全く違う内容な奴", likelihood=0.5),
    ]
    result = mmr_rank(candidates, k=2, lambda_param=0.1)
    assert len(result) == 2
    # 最尤の候補は必ず選ばれる
    assert result[0].title == "挨拶が長い奴"
    # 多様性を重視すると、似た候補より違う内容の候補が選ばれる
    assert result[1].title == "全く違う内容な奴"


def test_mmr_rank_handles_empty():
    assert mmr_rank([], k=5) == []


def test_mmr_rank_k_zero():
    candidates = [ScoredCandidate(title="な奴", likelihood=1.0)]
    assert mmr_rank(candidates, k=0) == []


def test_mmr_rank_k_larger_than_candidates():
    candidates = [ScoredCandidate(title="な奴", likelihood=1.0)]
    result = mmr_rank(candidates, k=5)
    assert len(result) == 1
