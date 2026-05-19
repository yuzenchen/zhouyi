"""to_localized() 雙語切換邏輯。"""
from app.models.hexagram import to_localized


SAMPLE = {
    "sequence": 1, "inner": 7, "outer": 7,
    "name_zh": "乾", "name_en": "Qian",
    "judgment_zh": "元、亨、利、貞。", "judgment_en": "The Creative works sublime success.",
    "image_zh": "天行健,君子以自強不息。", "image_en": "Heaven moves with strength.",
    "lines": [
        {"position": 1, "text_zh": "潛龍勿用。", "text_en": "Hidden dragon. Do not act."},
        {"position": 2, "text_zh": "見龍在田。", "text_en": "Dragon in the field."},
    ],
}


def test_zh_picks_zh_fields():
    out = to_localized(SAMPLE, "zh-TW")
    assert out["name"] == "乾"
    assert "元" in out["judgment"]
    assert "天行健" in out["image"]
    assert out["lines"][0]["text"] == "潛龍勿用。"


def test_en_picks_en_fields():
    out = to_localized(SAMPLE, "en")
    assert out["name"] == "Qian"
    assert "Creative" in out["judgment"]
    assert "Heaven" in out["image"]
    assert out["lines"][0]["text"] == "Hidden dragon. Do not act."


def test_falls_back_to_zh_when_en_empty():
    """en 欄位空字串時要 fallback 到 zh,避免顯示空白。"""
    sample = {**SAMPLE, "name_en": "", "judgment_en": ""}
    out = to_localized(sample, "en")
    assert out["name"] == "乾"  # fallback
    assert "元" in out["judgment"]


def test_handles_missing_image():
    sample = {**SAMPLE}
    sample.pop("image_zh")
    sample.pop("image_en")
    out = to_localized(sample, "zh-TW")
    assert out["image"] == ""
