"""占卜 API。"""
from datetime import datetime, timezone
import logging

from fastapi import APIRouter, Request

from app.database import get_database
from app.models.divination import DivinationCreateRequest, DivinationRecord
from app.models.hexagram import to_localized
from app.services import hexagram_service
from app.services.divination import cast_hexagram, line_meta
from app.services.geo import extract_client_ip, lookup_geo

router = APIRouter(prefix="/api/divinate", tags=["divination"])
logger = logging.getLogger(__name__)


@router.post("")
async def divinate(payload: DivinationCreateRequest, request: Request) -> dict:
    """
    擲一卦並回傳:本卦、動爻、變卦、地理時間資訊。同時寫入歷史。

    Body:
        session_id: 匿名 session UUID(前端從 localStorage 取得)
        question:   用戶問題(可選)
        lang:       'zh-TW' | 'en'
    """
    lang = payload.lang if payload.lang in ("zh-TW", "en") else "zh-TW"

    # 1) 取地理位置(失敗不阻塞占卜)
    ip = extract_client_ip(request)
    geo = await lookup_geo(ip) if ip else None

    # 時區優先序:前端 client_tz (Intl.DateTimeFormat) > geo.timezone > UTC
    # 理由:ip-api 對私有 IP/VPN 不可靠,瀏覽器回報的才是使用者實際時區
    from zoneinfo import ZoneInfo
    local_dt = datetime.now(tz=timezone.utc)
    for candidate in (payload.client_tz, geo.timezone if geo else None):
        if not candidate:
            continue
        try:
            local_dt = datetime.now(tz=ZoneInfo(candidate))
            break
        except Exception:
            continue

    # 2) 擲卦
    result = cast_hexagram()

    # 3) 查本卦
    inner, outer = result.primary_key
    primary = await hexagram_service.get_by_trigrams(inner, outer)
    primary_payload = to_localized(primary, lang) if primary else None

    # 4) 查變卦(若有動爻)
    transformed_payload = None
    if result.transformed_key:
        t_inner, t_outer = result.transformed_key
        transformed = await hexagram_service.get_by_trigrams(t_inner, t_outer)
        transformed_payload = to_localized(transformed, lang) if transformed else None

    # 5) 寫入歷史
    record = DivinationRecord(
        session_id=payload.session_id,
        question=payload.question,
        lines=result.lines,
        primary_inner=inner,
        primary_outer=outer,
        transformed_inner=result.transformed_key[0] if result.transformed_key else None,
        transformed_outer=result.transformed_key[1] if result.transformed_key else None,
        changing_indices=result.changing_indices,
        geo=geo or None,
        local_time=local_dt.strftime("%Y-%m-%d %H:%M:%S"),
        lang=lang,
    )
    db = get_database()
    insert_result = await db.divinations.insert_one(record.model_dump())

    return {
        "id": str(insert_result.inserted_id),
        "time": record.local_time,
        "geo": record.geo.model_dump() if record.geo else None,
        "lines": [line_meta(v, lang) for v in result.lines],
        "primary": primary_payload,
        "transformed": transformed_payload,
        "changing_indices": result.changing_indices,
        "lang": lang,
    }
