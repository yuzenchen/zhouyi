"""
六十四卦標準對照表。

八卦二進位編碼(下而上):
    0 = 坤 ☷ (000)    1 = 震 ☳ (001)    2 = 坎 ☵ (010)    3 = 兌 ☱ (011)
    4 = 艮 ☶ (100)    5 = 離 ☲ (101)    6 = 巽 ☴ (110)    7 = 乾 ☰ (111)

每一卦由「內卦(下卦)」與「外卦(上卦)」組成。
sequence 是周易通行本(序卦傳)的卦序 1~64。
"""

# 八卦資料:索引 = 二進位值
TRIGRAMS = [
    {"index": 0, "name_zh": "坤", "name_en": "Earth",    "symbol": "☷", "element": "地", "binary": "000"},
    {"index": 1, "name_zh": "震", "name_en": "Thunder",  "symbol": "☳", "element": "雷", "binary": "001"},
    {"index": 2, "name_zh": "坎", "name_en": "Water",    "symbol": "☵", "element": "水", "binary": "010"},
    {"index": 3, "name_zh": "兌", "name_en": "Lake",     "symbol": "☱", "element": "澤", "binary": "011"},
    {"index": 4, "name_zh": "艮", "name_en": "Mountain", "symbol": "☶", "element": "山", "binary": "100"},
    {"index": 5, "name_zh": "離", "name_en": "Fire",     "symbol": "☲", "element": "火", "binary": "101"},
    {"index": 6, "name_zh": "巽", "name_en": "Wind",     "symbol": "☴", "element": "風", "binary": "110"},
    {"index": 7, "name_zh": "乾", "name_en": "Heaven",   "symbol": "☰", "element": "天", "binary": "111"},
]

# 六十四卦對照:(inner, outer) -> {sequence, name_zh, name_en}
# inner = 內卦(下卦)二進位值,outer = 外卦(上卦)二進位值
HEXAGRAM_LOOKUP: dict[tuple[int, int], dict] = {
    # 序卦傳的卦序對應
    (7, 7): {"sequence": 1,  "name_zh": "乾",   "name_en": "Qian"},
    (0, 0): {"sequence": 2,  "name_zh": "坤",   "name_en": "Kun"},
    (1, 2): {"sequence": 3,  "name_zh": "屯",   "name_en": "Zhun"},
    (2, 4): {"sequence": 4,  "name_zh": "蒙",   "name_en": "Meng"},
    (7, 2): {"sequence": 5,  "name_zh": "需",   "name_en": "Xu"},
    (2, 7): {"sequence": 6,  "name_zh": "訟",   "name_en": "Song"},
    (2, 0): {"sequence": 7,  "name_zh": "師",   "name_en": "Shi"},
    (0, 2): {"sequence": 8,  "name_zh": "比",   "name_en": "Bi"},
    (7, 6): {"sequence": 9,  "name_zh": "小畜", "name_en": "Xiao Xu"},
    (3, 7): {"sequence": 10, "name_zh": "履",   "name_en": "Lu"},
    (7, 0): {"sequence": 11, "name_zh": "泰",   "name_en": "Tai"},
    (0, 7): {"sequence": 12, "name_zh": "否",   "name_en": "Pi"},
    (5, 7): {"sequence": 13, "name_zh": "同人", "name_en": "Tong Ren"},
    (7, 5): {"sequence": 14, "name_zh": "大有", "name_en": "Da You"},
    (4, 0): {"sequence": 15, "name_zh": "謙",   "name_en": "Qian (Modesty)"},
    (0, 1): {"sequence": 16, "name_zh": "豫",   "name_en": "Yu"},
    (1, 3): {"sequence": 17, "name_zh": "隨",   "name_en": "Sui"},
    (6, 4): {"sequence": 18, "name_zh": "蠱",   "name_en": "Gu"},
    (3, 0): {"sequence": 19, "name_zh": "臨",   "name_en": "Lin"},
    (0, 6): {"sequence": 20, "name_zh": "觀",   "name_en": "Guan"},
    (1, 5): {"sequence": 21, "name_zh": "噬嗑", "name_en": "Shi He"},
    (5, 4): {"sequence": 22, "name_zh": "賁",   "name_en": "Ben"},
    (0, 4): {"sequence": 23, "name_zh": "剝",   "name_en": "Bo"},
    (1, 0): {"sequence": 24, "name_zh": "復",   "name_en": "Fu"},
    (1, 7): {"sequence": 25, "name_zh": "無妄", "name_en": "Wu Wang"},
    (7, 4): {"sequence": 26, "name_zh": "大畜", "name_en": "Da Xu"},
    (1, 4): {"sequence": 27, "name_zh": "頤",   "name_en": "Yi (Nourishment)"},
    (6, 3): {"sequence": 28, "name_zh": "大過", "name_en": "Da Guo"},
    (2, 2): {"sequence": 29, "name_zh": "坎",   "name_en": "Kan"},
    (5, 5): {"sequence": 30, "name_zh": "離",   "name_en": "Li"},
    (4, 3): {"sequence": 31, "name_zh": "咸",   "name_en": "Xian"},
    (6, 1): {"sequence": 32, "name_zh": "恆",   "name_en": "Heng"},
    (4, 7): {"sequence": 33, "name_zh": "遯",   "name_en": "Dun"},
    (7, 1): {"sequence": 34, "name_zh": "大壯", "name_en": "Da Zhuang"},
    (0, 5): {"sequence": 35, "name_zh": "晉",   "name_en": "Jin"},
    (5, 0): {"sequence": 36, "name_zh": "明夷", "name_en": "Ming Yi"},
    (5, 6): {"sequence": 37, "name_zh": "家人", "name_en": "Jia Ren"},
    (3, 5): {"sequence": 38, "name_zh": "睽",   "name_en": "Kui"},
    (4, 2): {"sequence": 39, "name_zh": "蹇",   "name_en": "Jian (Obstruction)"},
    (2, 1): {"sequence": 40, "name_zh": "解",   "name_en": "Xie"},
    (3, 4): {"sequence": 41, "name_zh": "損",   "name_en": "Sun"},
    (1, 6): {"sequence": 42, "name_zh": "益",   "name_en": "Yi (Increase)"},
    (7, 3): {"sequence": 43, "name_zh": "夬",   "name_en": "Guai"},
    (6, 7): {"sequence": 44, "name_zh": "姤",   "name_en": "Gou"},
    (0, 3): {"sequence": 45, "name_zh": "萃",   "name_en": "Cui"},
    (6, 0): {"sequence": 46, "name_zh": "升",   "name_en": "Sheng"},
    (2, 3): {"sequence": 47, "name_zh": "困",   "name_en": "Kun (Oppression)"},
    (6, 2): {"sequence": 48, "name_zh": "井",   "name_en": "Jing"},
    (5, 3): {"sequence": 49, "name_zh": "革",   "name_en": "Ge"},
    (6, 5): {"sequence": 50, "name_zh": "鼎",   "name_en": "Ding"},
    (1, 1): {"sequence": 51, "name_zh": "震",   "name_en": "Zhen"},
    (4, 4): {"sequence": 52, "name_zh": "艮",   "name_en": "Gen"},
    (4, 6): {"sequence": 53, "name_zh": "漸",   "name_en": "Jian (Development)"},
    (3, 1): {"sequence": 54, "name_zh": "歸妹", "name_en": "Gui Mei"},
    (5, 1): {"sequence": 55, "name_zh": "豐",   "name_en": "Feng"},
    (4, 5): {"sequence": 56, "name_zh": "旅",   "name_en": "Lu (Wanderer)"},
    (6, 6): {"sequence": 57, "name_zh": "巽",   "name_en": "Xun"},
    (3, 3): {"sequence": 58, "name_zh": "兌",   "name_en": "Dui"},
    (2, 6): {"sequence": 59, "name_zh": "渙",   "name_en": "Huan"},
    (3, 2): {"sequence": 60, "name_zh": "節",   "name_en": "Jie"},
    (3, 6): {"sequence": 61, "name_zh": "中孚", "name_en": "Zhong Fu"},
    (4, 1): {"sequence": 62, "name_zh": "小過", "name_en": "Xiao Guo"},
    (5, 2): {"sequence": 63, "name_zh": "既濟", "name_en": "Ji Ji"},
    (2, 5): {"sequence": 64, "name_zh": "未濟", "name_en": "Wei Ji"},
}


def bin_lines_to_trigrams(bin_lines: list[int]) -> tuple[int, int]:
    """
    將六爻(初爻 → 上爻)二進位 list 轉換成 (內卦索引, 外卦索引)。

    bin_lines[0:3] = 內卦(下卦),bin_lines[3:6] = 外卦(上卦)
    每個三爻位置:bin_lines[0] 是初爻(最下),bin_lines[2] 是內卦的上爻

    回傳 (inner, outer) 可直接用 HEXAGRAM_LOOKUP 查表
    """
    if len(bin_lines) != 6:
        raise ValueError(f"Expected 6 lines, got {len(bin_lines)}")
    inner = bin_lines[0] + (bin_lines[1] << 1) + (bin_lines[2] << 2)
    outer = bin_lines[3] + (bin_lines[4] << 1) + (bin_lines[5] << 2)
    return inner, outer


def lookup_hexagram(bin_lines: list[int]) -> dict:
    """根據六爻直接查得卦象基本資訊。"""
    inner, outer = bin_lines_to_trigrams(bin_lines)
    return HEXAGRAM_LOOKUP[(inner, outer)]
