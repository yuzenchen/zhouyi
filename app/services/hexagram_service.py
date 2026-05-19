"""卦象資料庫查詢服務。"""
from typing import Optional

from app.database import get_database
from app.models.hexagram import Hexagram


async def get_by_trigrams(inner: int, outer: int) -> Optional[dict]:
    """根據內外卦索引查得單一卦象,回傳 dict(已包含 _id)。"""
    db = get_database()
    return await db.hexagrams.find_one({"inner": inner, "outer": outer}, {"_id": 0})


async def get_by_sequence(sequence: int) -> Optional[dict]:
    db = get_database()
    return await db.hexagrams.find_one({"sequence": sequence}, {"_id": 0})


async def list_all() -> list[dict]:
    """依序卦傳排序列出全部 64 卦,供卦象百科頁使用。"""
    db = get_database()
    cursor = db.hexagrams.find({}, {"_id": 0}).sort("sequence", 1)
    return [doc async for doc in cursor]


async def upsert(hexagram: Hexagram) -> None:
    """寫入或更新卦象資料(供 seed 腳本與管理介面使用)。"""
    db = get_database()
    await db.hexagrams.update_one(
        {"inner": hexagram.inner, "outer": hexagram.outer},
        {"$set": hexagram.model_dump()},
        upsert=True,
    )
