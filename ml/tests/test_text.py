from ml.common.text import ends_with_suffix, is_valid_length, normalize_title, strip_suffix


def test_normalize_removes_brackets():
    assert normalize_title("【企画】早口言葉が言えない奴") == "早口言葉が言えない奴"


def test_normalize_removes_hashtags():
    assert normalize_title("即興コントが下手な奴 #公式 #shorts") == "即興コントが下手な奴"


def test_normalize_removes_channel_name_suffix():
    assert normalize_title("変な自己紹介をする奴 / サンプルタワー") == "変な自己紹介をする奴"


def test_normalize_extracts_kagi_bracket_title():
    assert (
        normalize_title("『目ヂカラ強すぎ店員な奴』サンプル企画【SAMPLETOWER】")
        == "目ヂカラ強すぎ店員な奴"
    )


def test_normalize_extracts_nested_kagi_bracket_title():
    assert (
        normalize_title("『『カット』と『加藤』が紛らわしい映画監督な奴』サンプル企画【SAMPLETOWER】")
        == "『カット』と『加藤』が紛らわしい映画監督な奴"
    )


def test_normalize_strips_trailing_tilde_subtitle():
    assert (
        normalize_title("『友達作るの下手な奴〜アホ田とキショ田〜』サンプル企画【SAMPLETOWER】")
        == "友達作るの下手な奴"
    )
    assert (
        normalize_title("『ため口な奴～ベテラン刑事と新米刑事～』サンプル企画【SAMPLETOWER】")
        == "ため口な奴"
    )


def test_normalize_strips_trailing_part_number():
    assert normalize_title("『シュールなネタしそうな奴  パート２』サンプル企画【SAMPLETOWER】") == "シュールなネタしそうな奴"


def test_normalize_nfkc():
    assert normalize_title("ｶﾗｵｹが下手な奴") == "カラオケが下手な奴"


def test_ends_with_suffix():
    assert ends_with_suffix("遅刻する言い訳が下手な奴")
    assert not ends_with_suffix("遅刻する言い訳が下手な人")


def test_strip_suffix():
    assert strip_suffix("遅刻する言い訳が下手な奴") == "遅刻する言い訳が下手な"
    assert strip_suffix("該当なし") == "該当なし"


def test_is_valid_length():
    assert is_valid_length("短いな奴")
    assert not is_valid_length("な")
    assert not is_valid_length("あ" * 41)
