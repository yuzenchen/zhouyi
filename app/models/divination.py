"""占卜歷史記錄模型。"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GeoInfo(BaseModel):
    ip: str = ""
    country: str = ""
    region: str = ""
    city: str = ""
    timezone: str = ""
    lat: float | None = None
    lon: float | None = None


class DivinationRecord(BaseModel):
    """寫入 DB 的單次占卜記錄。"""
    session_id: str = Field(description="匿名 session,可用 cookie/localStorage UUID")
    question: str | None = None
    lines: list[int] = Field(description="六爻 6/7/8/9 list,初爻→上爻")
    primary_inner: int
    primary_outer: int
    transformed_inner: int | None = None
    transformed_outer: int | None = None
    changing_indices: list[int] = Field(default_factory=list)
    geo: GeoInfo = Field(default_factory=GeoInfo)
    local_time: str = ""
    lang: str = "zh-TW"
    ai_analysis: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DivinationCreateRequest(BaseModel):
    """前端打 /api/divinate 的請求(可選擇帶問題)。"""
    session_id: str
    question: str | None = None
    lang: str = "zh-TW"
    client_tz: str | None = Field(
        default=None,
        description="瀏覽器回報的 IANA timezone(如 Asia/Taipei),優先於 IP geo",
    )


class HistoryQuery(BaseModel):
    session_id: str
    limit: int = Field(default=20, ge=1, le=100)
