"""
測試占卜核心邏輯。
執行:pytest tests/ -v
"""
import pytest

from app.services.divination import cast_hexagram, line_meta, CHANGING_VALUES, YIN_VALUES
from app.utils.trigrams import HEXAGRAM_LOOKUP, bin_lines_to_trigrams


def test_64_hexagrams_unique():
    """64 卦對照表必須恰好覆蓋 8x8 = 64 個 (inner, outer) 組合,且 sequence 不重複。"""
    assert len(HEXAGRAM_LOOKUP) == 64
    sequences = [v["sequence"] for v in HEXAGRAM_LOOKUP.values()]
    assert sorted(sequences) == list(range(1, 65))


def test_trigram_keys_complete():
    """所有 (inner, outer) ∈ {0..7} × {0..7} 都必須有對應。"""
    for inner in range(8):
        for outer in range(8):
            assert (inner, outer) in HEXAGRAM_LOOKUP, f"missing ({inner}, {outer})"


def test_pure_hexagrams():
    """純卦驗證:乾(7,7) = 1,坤(0,0) = 2"""
    assert HEXAGRAM_LOOKUP[(7, 7)]["name_zh"] == "乾"
    assert HEXAGRAM_LOOKUP[(7, 7)]["sequence"] == 1
    assert HEXAGRAM_LOOKUP[(0, 0)]["name_zh"] == "坤"
    assert HEXAGRAM_LOOKUP[(0, 0)]["sequence"] == 2


def test_bin_lines_to_trigrams():
    """六爻全陽 → (7, 7),六爻全陰 → (0, 0)。"""
    assert bin_lines_to_trigrams([1, 1, 1, 1, 1, 1]) == (7, 7)
    assert bin_lines_to_trigrams([0, 0, 0, 0, 0, 0]) == (0, 0)
    # 內卦坎(010=2),外卦離(101=5)→ 第 63 卦既濟
    assert bin_lines_to_trigrams([0, 1, 0, 1, 0, 1]) == (2, 5)
    assert HEXAGRAM_LOOKUP[(2, 5)]["name_zh"] == "未濟"  # 注意:這裡是 inner=2 outer=5


def test_cast_returns_valid_result():
    """擲卦應產生 6 個 6/7/8/9 的值。"""
    result = cast_hexagram()
    assert len(result.lines) == 6
    for v in result.lines:
        assert v in (6, 7, 8, 9)
    # primary_key 必須是合法卦
    assert result.primary_key in HEXAGRAM_LOOKUP


def test_changing_lines_match():
    """changing_indices 必須對應 6 或 9 的位置。"""
    result = cast_hexagram()
    for idx in result.changing_indices:
        assert result.lines[idx] in CHANGING_VALUES


def test_transformed_only_when_changing():
    """有動爻才有變卦;無動爻時 transformed_key 為 None。"""
    # 多次擲卦驗證
    has_both_seen = {"with": False, "without": False}
    for _ in range(50):
        r = cast_hexagram()
        if r.changing_indices:
            assert r.transformed_key is not None
            assert r.transformed_key in HEXAGRAM_LOOKUP
            has_both_seen["with"] = True
        else:
            assert r.transformed_key is None
            has_both_seen["without"] = True
    # 50 次基本上會兩種都遇到(動爻機率不低)
    assert has_both_seen["with"], "Expected at least one cast with changing lines"


def test_randomness_no_same_second_collision():
    """兩次連續擲卦應產生不同結果(原版 bug 在這裡會撞)。"""
    r1 = cast_hexagram()
    r2 = cast_hexagram()
    # 雖然理論上有極小機率相同(1/4^6),但連續兩次完全相同的機率 < 1/4000
    assert r1.lines != r2.lines or r1.changing_indices != r2.changing_indices


def test_line_meta_localization():
    zh = line_meta(6, "zh-TW")
    en = line_meta(6, "en")
    assert zh["name"] == "老陰"
    assert en["name"] == "Old Yin"
    assert zh["yin"] is True
    assert zh["changing"] is True
