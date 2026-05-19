"""卦象資料模型。對應 MongoDB hexagrams collection。"""
from typing import Literal

from pydantic import BaseModel, Field


class HexagramLine(BaseModel):
    """單一爻辭。"""
    position: int = Field(ge=1, le=6, description="爻位 1=初爻 ... 6=上爻")
    text_zh: str
    text_en: str = ""


class Hexagram(BaseModel):
    """完整卦象資料。"""
    sequence: int = Field(ge=1, le=64, description="序卦傳卦序")
    inner: int = Field(ge=0, le=7, description="內卦索引(下卦)")
    outer: int = Field(ge=0, le=7, description="外卦索引(上卦)")
    name_zh: str
    name_en: str
    judgment_zh: str = Field(description="卦辭(彖辭)中文")
    judgment_en: str = ""
    image_zh: str = Field(default="", description="象辭(大象傳)")
    image_en: str = ""
    lines: list[HexagramLine] = Field(default_factory=list, description="六爻爻辭")

    @property
    def trigram_key(self) -> tuple[int, int]:
        return (self.inner, self.outer)


class HexagramPublic(Hexagram):
    """對外回傳的卦象資料,根據 lang 篩選欄位。"""
    pass


def to_localized(h: Hexagram | dict, lang: Literal["zh-TW", "en"] = "zh-TW") -> dict:
    """依語言把雙語欄位收斂成單一欄位,供前端使用。"""
    if isinstance(h, Hexagram):
        h = h.model_dump()
    suffix = "zh" if lang.startswith("zh") else "en"
    out = {
        "sequence": h["sequence"],
        "inner": h["inner"],
        "outer": h["outer"],
        "name": h.get(f"name_{suffix}") or h.get("name_zh"),
        "judgment": h.get(f"judgment_{suffix}") or h.get("judgment_zh"),
        "image": h.get(f"image_{suffix}") or h.get("image_zh", ""),
        "lines": [
            {
                "position": ln["position"],
                "text": ln.get(f"text_{suffix}") or ln.get("text_zh", ""),
            }
            for ln in h.get("lines", [])
        ],
    }
    return out
