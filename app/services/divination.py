"""
蓍草法占卜核心邏輯。

修正原版的 bug:
  - 原本 seed = YYYYMMDDHHMMSS,同秒占卜會撞卦
  - 改用 secrets.SystemRandom (cryptographic-grade) + 微秒
  - 原本沒處理「動爻」與「變卦」(本卦六爻全變後得到的卦)
"""
import secrets
from dataclasses import dataclass

from app.utils.trigrams import HEXAGRAM_LOOKUP, bin_lines_to_trigrams

# 老陰 = 6,可變;少陽 = 7,不變;少陰 = 8,不變;老陽 = 9,可變
YIN_VALUES = {6, 8}
CHANGING_VALUES = {6, 9}  # 動爻

# 爻名稱(供前端 i18n 使用)
LINE_NAMES = {
    6: {"zh": "老陰", "en": "Old Yin",     "yin": True,  "changing": True},
    7: {"zh": "少陽", "en": "Young Yang",  "yin": False, "changing": False},
    8: {"zh": "少陰", "en": "Young Yin",   "yin": True,  "changing": False},
    9: {"zh": "老陽", "en": "Old Yang",    "yin": False, "changing": True},
}


@dataclass
class DivinationResult:
    """單次占卜結果。"""

    lines: list[int]              # 6, 7, 8, 9 的 list,初爻 → 上爻
    primary_key: tuple[int, int]  # 本卦 (inner, outer)
    changing_indices: list[int]   # 動爻位置(0-indexed,初爻為 0)
    transformed_key: tuple[int, int] | None  # 變卦,若無動爻則為 None


def _rng() -> secrets.SystemRandom:
    """每次占卜建立獨立 SystemRandom 實例,避免 race condition。"""
    return secrets.SystemRandom()


def yarrow_stalk_one_line(rng: secrets.SystemRandom) -> int:
    """
    傳統蓍草法產生一爻。三變得一爻,結果 ∈ {6, 7, 8, 9}。

    使用 secrets.SystemRandom 取得 OS-level 熵源,
    比 random.Random 更適合占卜這種「不可預測」場景。
    """
    stalks = 49  # 50 莖去其一不用
    for _ in range(3):
        left = rng.randint(1, stalks - 1)
        right = stalks - left
        right -= 1  # 掛一(從右堆取一)
        remainder1 = left % 4 or 4
        remainder2 = right % 4 or 4
        stalks -= 1 + remainder1 + remainder2
    return stalks // 4


def cast_hexagram() -> DivinationResult:
    """完整擲卦:得六爻,計算動爻與變卦。"""
    rng = _rng()
    # 初爻 → 上爻 (六次)
    lines = [yarrow_stalk_one_line(rng) for _ in range(6)]

    # 二進位化:陽爻 = 1,陰爻 = 0
    bin_lines = [0 if v in YIN_VALUES else 1 for v in lines]
    primary_key = bin_lines_to_trigrams(bin_lines)

    # 計算動爻位置
    changing = [i for i, v in enumerate(lines) if v in CHANGING_VALUES]

    # 變卦:動爻翻轉(陰↔陽),非動爻不變
    transformed_key: tuple[int, int] | None = None
    if changing:
        transformed_bin = [
            (1 - b) if i in changing else b for i, b in enumerate(bin_lines)
        ]
        transformed_key = bin_lines_to_trigrams(transformed_bin)

    return DivinationResult(
        lines=lines,
        primary_key=primary_key,
        changing_indices=changing,
        transformed_key=transformed_key,
    )


def line_meta(value: int, lang: str = "zh-TW") -> dict:
    """爻的中繼資料,供 API response 使用。"""
    info = LINE_NAMES[value]
    key = "zh" if lang.startswith("zh") else "en"
    return {
        "value": value,
        "name": info[key],
        "yin": info["yin"],
        "changing": info["changing"],
    }
