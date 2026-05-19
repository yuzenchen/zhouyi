"""占卜歷史 API。匿名 session 對應一個用戶的歷史。"""
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.database import get_database
from app.services import hexagram_service
from app.models.hexagram import to_localized

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("")
async def list_history(
    session_id: str = Query(..., min_length=8),
    limit: int = Query(20, ge=1, le=100),
    lang: str = Query("zh-TW"),
) -> list[dict]:
    """取得指定 session 的最近 N 次占卜。回傳已附上卦名以便列表呈現。"""
    db = get_database()
    cursor = db.divinations.find(
        {"session_id": session_id},
        {"_id": 1, "lines": 1, "primary_inner": 1, "primary_outer": 1,
         "changing_indices": 1, "question": 1, "local_time": 1, "created_at": 1},
    ).sort("created_at", -1).limit(limit)

    docs = [doc async for doc in cursor]

    # 補上卦名
    out = []
    for d in docs:
        primary = await hexagram_service.get_by_trigrams(d["primary_inner"], d["primary_outer"])
        out.append({
            "id": str(d["_id"]),
            "question": d.get("question"),
            "local_time": d.get("local_time"),
            "created_at": d.get("created_at").isoformat() if d.get("created_at") else None,
            "lines": d["lines"],
            "changing_indices": d.get("changing_indices", []),
            "primary": to_localized(primary, lang) if primary else None,
        })
    return out


@router.get("/{record_id}")
async def get_history_detail(
    record_id: str,
    session_id: str = Query(..., min_length=8),
    lang: str = Query("zh-TW"),
) -> dict:
    """單筆歷史詳情。需提供同一 session_id 才能讀取,確保隔離。"""
    from bson import ObjectId
    try:
        oid = ObjectId(record_id)
    except Exception:
        raise HTTPException(400, "invalid id")

    db = get_database()
    doc = await db.divinations.find_one({"_id": oid, "session_id": session_id})
    if not doc:
        raise HTTPException(404, "not found")

    primary = await hexagram_service.get_by_trigrams(doc["primary_inner"], doc["primary_outer"])
    transformed = None
    if doc.get("transformed_inner") is not None and doc.get("transformed_outer") is not None:
        transformed = await hexagram_service.get_by_trigrams(
            doc["transformed_inner"], doc["transformed_outer"]
        )

    return {
        "id": str(doc["_id"]),
        "question": doc.get("question"),
        "local_time": doc.get("local_time"),
        "lines": doc["lines"],
        "changing_indices": doc.get("changing_indices", []),
        "geo": doc.get("geo"),
        "primary": to_localized(primary, lang) if primary else None,
        "transformed": to_localized(transformed, lang) if transformed else None,
        "ai_analysis": doc.get("ai_analysis"),
    }


@router.delete("/{record_id}")
async def delete_record(record_id: str, session_id: str = Query(...)) -> dict:
    """刪除一筆歷史(限同 session 才能刪)。"""
    from bson import ObjectId
    try:
        oid = ObjectId(record_id)
    except Exception:
        raise HTTPException(400, "invalid id")
    db = get_database()
    result = await db.divinations.delete_one({"_id": oid, "session_id": session_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "not found or not authorized")
    return {"deleted": True}
