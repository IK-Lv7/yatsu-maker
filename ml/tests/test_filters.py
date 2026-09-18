from ml.generate.filters import contains_ng_word, is_appropriate, matches_format


def test_matches_format_requires_suffix():
    assert matches_format("遅刻する言い訳が下手な奴")
    assert not matches_format("遅刻する言い訳が下手な人")


def test_matches_format_length_bounds():
    assert not matches_format("な奴", min_len=3)
    assert not matches_format("あ" * 41 + "な奴", max_len=40)


def test_matches_format_rejects_url():
    assert not matches_format("http://example.com を貼る奴")


def test_contains_ng_word_detects_match():
    assert contains_ng_word("死ねと言う奴", ["死ね"]) == "死ね"


def test_contains_ng_word_no_match():
    assert contains_ng_word("普通に挨拶する奴", ["死ね"]) is None


def test_is_appropriate_blocks_ng_word():
    assert not is_appropriate("死ねと言う奴", ng_words=["死ね"])


def test_is_appropriate_allows_clean_text():
    assert is_appropriate("挨拶がやたら丁寧な奴", ng_words=["死ね"])
