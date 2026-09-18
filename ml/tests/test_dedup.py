from ml.generate.dedup import (
    filter_duplicates,
    is_exact_duplicate,
    is_near_duplicate_embedding,
    is_near_duplicate_lexical,
)


def test_is_exact_duplicate():
    assert is_exact_duplicate("挨拶が長い奴", {"挨拶が長い奴", "別のタイトル"})
    assert not is_exact_duplicate("挨拶が短い奴", {"挨拶が長い奴"})


def test_is_near_duplicate_lexical():
    assert is_near_duplicate_lexical("挨拶がやたら長い奴", ["挨拶がやたら長いな奴"], threshold=0.8)
    assert not is_near_duplicate_lexical("全く違う内容の奴", ["挨拶がやたら長い奴"], threshold=0.8)


def test_is_near_duplicate_embedding_uses_embed_fn():
    def fake_embed(texts):
        # 完全に同じベクトルを返す=常に類似度1.0
        return [[1.0, 0.0] for _ in texts]

    assert is_near_duplicate_embedding("新しい奴", ["既存の奴"], fake_embed, threshold=0.9)


def test_filter_duplicates_removes_exact_and_lexical():
    candidates = ["挨拶が長い奴", "全く新しい奴", "挨拶がやたら長い奴"]
    existing = ["挨拶が長い奴"]
    result = filter_duplicates(candidates, existing, lexical_threshold=0.8)
    assert "挨拶が長い奴" not in result
    assert "挨拶がやたら長い奴" not in result
    assert "全く新しい奴" in result
