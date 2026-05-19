"""卦象百科 API:列出 / 查單卦。"""
from fastapi import APIRouter, HTTPException, Query

from app.models.hexagram import to_localized
from app.services import hexagram_service

router = APIRouter(prefix="/api/hexagrams", tags=["hexagrams"])


@router.get("")
async def list_hexagrams(lang: str = Query("zh-TW")) -> list[dict]:
    """列出全部 64 卦,依序卦傳排序。"""
    docs = await hexagram_service.list_all()
    return [to_localized(d, lang) for d in docs]


@router.get("/{sequence}")
async def get_hexagram(sequence: int, lang: str = Query("zh-TW")) -> dict:
    """依卦序取得單卦。"""
    if not 1 <= sequence <= 64:
        raise HTTPException(400, "sequence must be 1..64")
    doc = await hexagram_service.get_by_sequence(sequence)
    if not doc:
        raise HTTPException(404, "Hexagram not found (DB may not be seeded)")
    return to_localized(doc, lang)
