"""AI 解卦代理。轉發到 n8n webhook,並選擇性把結果寫回對應的占卜記錄。"""
import logging
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import get_settings
from app.database import get_database

router = APIRouter(prefix="/api/ai-analysis", tags=["ai"])
logger = logging.getLogger(__name__)


class AIRequest(BaseModel):
    """前端傳入的 AI 解析請求。"""
    record_id: Optional[str] = None  # 若提供,會把結果寫回該筆 divination
    question: str
    gua_name: str
    gua_text: str
    yao_list: list = []
    lang: str = "zh-TW"


@router.post("")
async def ai_analysis(payload: AIRequest) -> dict:
    settings = get_settings()
    if not settings.n8n_ai_webhook:
        raise HTTPException(503, "AI analysis webhook not configured")

    try:
        async with httpx.AsyncClient(timeout=40.0) as client:
            resp = await client.post(
                settings.n8n_ai_webhook,
                json=payload.model_dump(exclude={"record_id"}),
            )
    except httpx.RequestError as e:
        logger.error("AI webhook call failed: %s", e)
        raise HTTPException(502, f"AI webhook error: {e}")

    try:
        result = resp.json()
    except Exception:
        logger.error("AI webhook non-JSON response: %s", resp.text[:200])
        raise HTTPException(502, "AI webhook returned non-JSON")

    # 若有 record_id,把分析結果寫回占卜記錄
    if payload.record_id:
        from bson import ObjectId
        try:
            oid = ObjectId(payload.record_id)
            db = get_database()
            analysis_text = result.get("analysis") or result.get("text") or str(result)
            await db.divinations.update_one(
                {"_id": oid},
                {"$set": {"ai_analysis": analysis_text}},
            )
        except Exception as e:
            logger.warning("Failed to persist ai_analysis: %s", e)

    return result
